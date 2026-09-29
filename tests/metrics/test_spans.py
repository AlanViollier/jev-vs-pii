"""Word-level and exact span scoring on hand-computed cases; exact matching agrees with nervaluate."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from nervaluate import Evaluator  # type: ignore[import-untyped]  # ships no type hints

from pii_bench.metrics.spans import (
    DocCounts,
    cleared_hits,
    doc_counts,
    gold_hits_by,
    predicted_hits_by_type,
    score_spans,
    scores_from_counts,
)
from pii_bench.schema import Doc, Span

_TEXT = "Send it to Marie Dupont at 12 rue des Lilas, Lyon today."


def _span(text: str, value: str, label: str | None = None) -> Span:
    start = text.index(value)
    return Span(start=start, end=start + len(value), label=label)


def _doc(gold: list[Span], text: str = _TEXT) -> Doc:
    return Doc(id="d", dataset="ai4privacy", split="test", text=text, gold=tuple(gold))


_GOLD = [
    _span(_TEXT, "Marie Dupont", "PERSON"),
    _span(_TEXT, "12 rue des Lilas", "LOCATION"),
    _span(_TEXT, "Lyon", "LOCATION"),
]


def test_one_span_over_street_and_city_loses_no_word() -> None:
    pred = [_span(_TEXT, "Marie Dupont"), _span(_TEXT, "12 rue des Lilas, Lyon")]
    assert doc_counts(_doc(_GOLD), pred, "word") == DocCounts(tp=7, fp=0, fn=0)
    assert doc_counts(_doc(_GOLD), pred, "exact") == DocCounts(tp=1, fp=1, fn=2)


def test_half_masked_name_counts_the_leak() -> None:
    pred = [_span(_TEXT, "Marie")]
    assert doc_counts(_doc(_GOLD[:1]), pred, "word") == DocCounts(tp=1, fp=0, fn=1)


def test_whole_doc_span_pays_in_precision() -> None:
    pred = [Span(start=0, end=len(_TEXT))]
    scores = score_spans([_doc(_GOLD)], [pred], "word")
    assert scores.recall == 1.0
    assert scores.precision == pytest.approx(7 / 12)


def test_typed_word_match_needs_the_same_label() -> None:
    pred = [_span(_TEXT, "Marie Dupont", "PERSON"), _span(_TEXT, "Lyon", "PERSON")]
    assert doc_counts(_doc(_GOLD), pred, "word", typed=True) == DocCounts(tp=2, fp=1, fn=5)
    assert doc_counts(_doc(_GOLD), pred, "word") == DocCounts(tp=3, fp=0, fn=4)


def test_scores_from_counts_micro_averages() -> None:
    scores = scores_from_counts([DocCounts(tp=3, fp=1, fn=0), DocCounts(tp=1, fp=0, fn=4)])
    assert (scores.tp, scores.fp, scores.fn) == (4, 1, 4)
    assert scores.precision == pytest.approx(0.8)
    assert scores.recall == pytest.approx(0.5)
    assert scores.f1 == pytest.approx(2 * 0.8 * 0.5 / 1.3)
    assert scores.f2 == pytest.approx(5 * 0.8 * 0.5 / (4 * 0.8 + 0.5))


def test_nothing_predicted_nothing_gold_scores_zero_not_nan() -> None:
    scores = scores_from_counts([DocCounts(tp=0, fp=0, fn=0)])
    assert (scores.precision, scores.recall, scores.f1, scores.f2) == (0.0, 0.0, 0.0, 0.0)


def test_gold_hits_group_gold_words_for_untyped_lanes() -> None:
    pred = [_span(_TEXT, "Marie Dupont"), _span(_TEXT, "Lyon")]
    assert gold_hits_by([_doc(_GOLD)], [pred], key=lambda span: span.label) == {
        "PERSON": (2, 2),
        "LOCATION": (1, 5),
    }


def test_predicted_hits_measure_each_claimed_type() -> None:
    pred = [
        _span(_TEXT, "Marie Dupont", "PERSON"),
        _span(_TEXT, "today", "DATETIME"),
        _span(_TEXT, "Lyon"),
    ]
    assert predicted_hits_by_type([_doc(_GOLD)], [pred]) == {"PERSON": (2, 2), "DATETIME": (0, 1)}


def test_docs_and_predictions_must_line_up() -> None:
    with pytest.raises(ValueError):
        score_spans([_doc(_GOLD)], [], "word")


@st.composite
def _disjoint_spans(draw: st.DrawFn) -> list[Span]:
    cuts = sorted(draw(st.sets(st.integers(0, 60), max_size=12)))
    pairs = list(zip(cuts[::2], cuts[1::2], strict=False))
    return [Span(start=a, end=b, label=draw(st.sampled_from(["PERSON", "ID"]))) for a, b in pairs]


@settings(max_examples=100)
@given(_disjoint_spans(), _disjoint_spans(), st.booleans())
def test_exact_matches_nervaluate(gold: list[Span], pred: list[Span], typed: bool) -> None:
    doc = _doc(gold, text="x" * 60)
    ours = doc_counts(doc, pred, "exact", typed=typed)
    as_dicts = [
        [{"label": s.label, "start": s.start, "end": s.end} for s in spans]
        for spans in (gold, pred)
    ]
    theirs = Evaluator(
        [as_dicts[0]], [as_dicts[1]], tags=["PERSON", "ID"], loader="dict"
    ).evaluate()
    counts = theirs["overall"]["strict" if typed else "exact"]
    assert ours.tp == counts.correct
    assert ours.tp + ours.fp == counts.actual
    assert ours.tp + ours.fn == counts.possible


def test_cleared_hits_count_masking_of_what_the_annotator_left_in_clear() -> None:
    text = "Ivo Brandt sued Norway before the Court of Appeal"
    doc = Doc(
        id="d",
        dataset="tab",
        split="test",
        text=text,
        gold=(_span(text, "Ivo Brandt", "PERSON"),),
        subject="Ivo Brandt",
        cleared=(_span(text, "Norway"), _span(text, "Court of Appeal")),
    )
    pred = [_span(text, "Ivo Brandt"), _span(text, "Norway")]
    assert cleared_hits([doc], [pred]) == (1, 4)
