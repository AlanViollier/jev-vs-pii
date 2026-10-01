"""Runner, store, tiers, tuning and result rows on tiny hand-made docs."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from jev_vs_pii.decode import DecodeParams, Threshold, Viterbi
from jev_vs_pii.lanes.mask_all import MaskAllLane
from jev_vs_pii.lanes.regex import RegexLane
from jev_vs_pii.metrics.results import human_lane_run, score_lane_run
from jev_vs_pii.report.export import (
    curve_records,
    example_records,
    headline_records,
    paired_records,
)
from jev_vs_pii.report.markdown import results_markdown
from jev_vs_pii.report.tables import hits_table, pareto_frontier
from jev_vs_pii.run import (
    TunedDecoder,
    headline_decoder,
    load_lane_runs,
    load_tuned,
    ranked,
    run_lane,
    save_lane_run,
    save_tuned,
    select_docs,
    tune_lane_run,
)
from jev_vs_pii.schema import Dataset, Doc, LaneInfo, LaneRun, Prediction, Span, Split, WordScore
from jev_vs_pii.words import split_words

_TEXT = "Mail ann@example.org or call Ann Lee today."


def _doc(i: int, split: Split = "dev", others: tuple[tuple[Span, ...], ...] = ()) -> Doc:
    email = Span(start=5, end=20, label="CONTACT")
    name = Span(start=29, end=36, label="PERSON")
    return Doc(
        id=f"d{i}",
        dataset="tab",
        split=split,
        text=_TEXT,
        gold=(email, name),
        other_annotators=others,
        subject="Ann Lee",
    )


def _lane_run(predictions: list[Prediction], split: Split = "dev") -> LaneRun:
    return LaneRun(
        run_id="r",
        lane=LaneInfo(id="jev_words", family="jev"),
        dataset="tab",
        split=split,
        tier="pilot",
        started_at=datetime(2026, 9, 29),
        wall_clock_s=1.0,
        predictions=tuple(predictions),
    )


def _scored(doc: Doc, probs: dict[str, float]) -> Prediction:
    """A per-word prediction scoring each named word, every other word 0.05."""
    scores = tuple(WordScore(p_pii=probs.get(w.text, 0.05)) for w in split_words(doc.text))
    return Prediction(doc_id=doc.id, lane_id="jev_words", spans=(), word_scores=scores)


def test_tiers_are_prefixes_of_each_other() -> None:
    docs = [_doc(i) for i in range(30)]
    smoke, pilot, full = (select_docs(docs, tier) for tier in ("smoke", "pilot", "full"))
    assert (len(smoke), len(pilot), len(full)) == (2, 20, 30)
    assert pilot[:2] == smoke and full[:20] == pilot


def test_runner_keeps_doc_order_reports_each_doc_and_times_local_lanes() -> None:
    docs = [_doc(i) for i in range(5)]
    seen: list[str] = []
    predictions = asyncio.run(
        run_lane(
            RegexLane(), docs, concurrency=2, on_prediction=lambda _, doc, __: seen.append(doc.id)
        )
    )
    assert [p.doc_id for p in predictions] == [d.id for d in docs]
    assert sorted(seen) == [d.id for d in docs]
    assert all(p.usage.latency_s > 0 for p in predictions)


def test_store_round_trips_and_names_llm_lanes_safely(tmp_path: Path) -> None:
    lane_run = _lane_run([_scored(_doc(0), {})]).model_copy(
        update={"lane": LaneInfo(id="llm_sayback:qwen3-30b", family="llm")}
    )
    path = save_lane_run(tmp_path, lane_run)
    assert ":" not in path.name
    assert load_lane_runs(tmp_path) == [lane_run]


def test_tuning_finds_the_cutoff_that_catches_a_low_scored_name() -> None:
    docs = [_doc(i) for i in range(3)]
    ## The model is sure about the email, lukewarm about the name: F2 wants the name in.
    run = _lane_run([_scored(d, {"ann@example.org": 0.9, "Ann": 0.3, "Lee": 0.3}) for d in docs])
    best = tune_lane_run(run, docs)
    params, f2 = best["threshold"]
    assert isinstance(params, Threshold) and params.cutoff <= 0.3
    assert f2 == pytest.approx(1.0)
    assert [d.dev_f2 for d in ranked(best)] == sorted((f for _, f in best.values()), reverse=True)


def test_headline_is_the_tuned_threshold_even_when_another_kind_won_on_dev() -> None:
    viterbi = TunedDecoder(params=Viterbi(), dev_f2=0.9)
    threshold = TunedDecoder(params=Threshold(cutoff=0.2), dev_f2=0.8)
    assert headline_decoder([viterbi, threshold]) is threshold
    assert headline_decoder([viterbi]) is None


def test_tuning_refuses_the_test_split() -> None:
    docs = [_doc(0, split="test")]
    with pytest.raises(ValueError, match="dev only"):
        tune_lane_run(_lane_run([_scored(docs[0], {})], split="test"), docs)


def test_tuned_decoders_round_trip_and_default_to_empty(tmp_path: Path) -> None:
    path = tmp_path / "decoders.json"
    assert load_tuned(path) == {}
    docs = [_doc(0)]
    tuned = {"jev_words": {"tab": ranked(tune_lane_run(_lane_run([_scored(docs[0], {})]), docs))}}
    save_tuned(path, tuned)  # type: ignore[arg-type]  # literal dict keys are a Dataset
    assert load_tuned(path) == tuned


def test_result_rows_redecode_with_a_decoder_and_carry_calibration() -> None:
    doc = _doc(0)
    run = _lane_run([_scored(doc, {"ann@example.org": 0.9, "Ann": 0.3, "Lee": 0.3})])
    default = score_lane_run(run, [doc])
    tuned = score_lane_run(run, [doc], Threshold(cutoff=0.25), headline=False)
    assert [row.mode for row in default] == ["word", "exact"]
    assert default[0].scores.recall == 0.0  # the lane's own spans are empty
    assert tuned[0].scores.recall == 1.0
    assert tuned[0].decoder == "threshold cutoff=0.25" and not tuned[0].headline
    assert default[0].ece is not None and default[0].brier is not None


def test_floor_scores_perfect_recall_and_no_calibration() -> None:
    doc = _doc(0)
    prediction = asyncio.run(MaskAllLane().predict(doc))
    (word, exact) = score_lane_run(_lane_run([prediction]), [doc])
    assert word.scores.recall == 1.0 and word.ece is None
    assert exact.scores.tp == 0


def test_human_row_uses_the_second_annotator_on_docs_that_have_one() -> None:
    second = (Span(start=29, end=36, label="PERSON"),)
    docs = [_doc(0, others=(second,)), _doc(1)]
    human = human_lane_run(docs)
    assert human is not None
    assert [p.doc_id for p in human.predictions] == ["d0"]
    (word, _) = score_lane_run(human, docs)
    assert (word.scores.precision, word.scores.recall) == (1.0, 2 / 3)
    assert human_lane_run([_doc(2)]) is None


def test_rows_carry_per_doc_results_hit_counts_curves_and_tab_errors() -> None:
    docs = [_doc(0), _doc(1)]
    run = _lane_run([_scored(d, {"ann@example.org": 0.9, "Ann": 0.3, "Lee": 0.3}) for d in docs])
    (word, exact) = score_lane_run(run, docs, Threshold(cutoff=0.5))
    assert [d.doc_id for d in word.per_doc] == ["d0", "d1"]
    assert word.gold_by_type == {"CONTACT": (2, 2), "PERSON": (0, 4)}
    assert word.top_missed == (("ann lee", 2),)
    ## Curves describe raw word scores, so only the undecoded row has them.
    assert word.threshold_curve is None
    (raw, _) = score_lane_run(run, docs)
    assert raw.threshold_curve is not None and raw.reliability is not None


def test_results_page_has_every_section_and_a_paired_comparison() -> None:
    docs = [_doc(i) for i in range(3)]
    jev = _lane_run([_scored(d, {"ann@example.org": 0.9, "Ann": 0.6, "Lee": 0.6}) for d in docs])
    regex = _lane_run([asyncio.run(RegexLane().predict(d)) for d in docs]).model_copy(
        update={"lane": LaneInfo(id="regex", family="rules")}
    )
    rows = [
        *score_lane_run(jev, docs, Threshold(cutoff=0.5)),
        *score_lane_run(regex, docs),
    ]
    page = results_markdown(rows)
    for section in (
        "Word level",
        "paired bootstrap",
        "Cost and time",
        "DIRECT",
        "Format vs context",
        "Every decoder on per-word scores",
        "Exact span",
    ):
        assert section in page
    assert "| regex | -" in page
    assert pareto_frontier([row for row in rows if row.mode == "word"]) == {
        "jev_words · threshold cutoff=0.5"
    }


def test_a_label_table_with_no_big_enough_label_says_so() -> None:
    doc = _doc(0)
    rows = score_lane_run(_lane_run([_scored(doc, {})]), [doc])
    assert hits_table(rows, lambda row: row.gold_by_type, min_total=1000).startswith("No group")


def test_headline_table_carries_the_caveats_of_the_lanes_in_it() -> None:
    doc = _doc(0)
    rows = score_lane_run(_lane_run([_scored(doc, {})]), [doc])
    llm = [
        row.model_copy(update={"lane": LaneInfo(id="llm_sayback:x", family="llm")}) for row in rows
    ]
    page = results_markdown(llm)
    assert "counts as finding nothing" in page
    assert "Privacy Filter" not in page


def test_export_lists_headline_rows_and_pairs_every_lane_with_the_best_jev() -> None:
    docs = [_doc(i, split="test") for i in range(3)]
    jev = _lane_run(
        [_scored(d, {"ann@example.org": 0.9, "Ann": 0.9, "Lee": 0.9}) for d in docs], split="test"
    )
    regex = asyncio.run(run_lane(RegexLane(), docs, concurrency=1))
    regex_run = jev.model_copy(update={"lane": RegexLane.info, "predictions": tuple(regex)})
    rows = [
        *score_lane_run(jev, docs, headline=False),
        *score_lane_run(jev, docs, Threshold(cutoff=0.5)),
        *score_lane_run(regex_run, docs),
    ]
    headline = headline_records(rows)
    assert sorted(record["lane"] for record in headline) == ["jev_words", "regex"]
    assert [(p["lane"], p["reference"]) for p in paired_records(rows)] == [("regex", "jev_words")]
    assert [c["lane"] for c in curve_records(rows)] == ["jev_words"]


def test_examples_never_show_ai4privacy_text_and_decode_per_word_lanes() -> None:
    doc = _doc(0, split="test")
    jev = _lane_run([_scored(doc, {"Ann": 0.9, "Lee": 0.9})], split="test")
    hidden = jev.model_copy(update={"dataset": "ai4privacy"})
    decoders: dict[tuple[str, Dataset], DecodeParams] = {("jev_words", "tab"): Threshold()}
    examples = example_records([jev, hidden], {"tab": [doc], "ai4privacy": [doc]}, decoders)
    assert [e["dataset"] for e in examples] == ["tab"]
    spans = examples[0]["lanes"]["jev_words"]["spans"]
    assert [doc.text[s["start"] : s["end"]] for s in spans] == ["Ann Lee"]
    lane = examples[0]["lanes"]["jev_words"]
    assert (lane["tp"], lane["fp"], lane["fn"]) == (2, 0, 1)  # the email is missed
    assert examples[0]["gold_words"] == [False, True, False, False, True, True, False]
    assert lane["masked"] == [False, False, False, False, True, True, False]
