"""Score a stored lane run into result rows: accuracy with CIs, calibration, per-type recall, cost."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from jev_vs_pii.decode import DecodeParams, decode, describe
from jev_vs_pii.metrics.bootstrap import bootstrap_ci
from jev_vs_pii.metrics.calibration import brier, ece, reliability_bins
from jev_vs_pii.metrics.cost import cost_summary
from jev_vs_pii.metrics.curve import threshold_curve
from jev_vs_pii.metrics.errors import top_errors
from jev_vs_pii.metrics.spans import (
    DocCounts,
    cleared_hits,
    doc_counts,
    gold_hits_by,
    predicted_hits_by_type,
    scores_from_counts,
)
from jev_vs_pii.metrics.tab_official import tab_official_scores
from jev_vs_pii.schema import (
    Doc,
    DocResult,
    LaneRun,
    MatchMode,
    Prediction,
    ResultRow,
    Span,
)
from jev_vs_pii.taxonomy import shape
from jev_vs_pii.words import covering_spans, split_words

MODES: tuple[MatchMode, ...] = ("word", "exact")

## Datasets whose licence lets their text appear in published results; ai4privacy's doesn't.
## Dev results are never published, so they show every dataset's strings.
_STRINGS_PUBLISHABLE = frozenset({"tab", "nemotron"})


def score_lane_run(
    lane_run: LaneRun,
    docs: Sequence[Doc],
    decoder: DecodeParams | None = None,
    seed: int = 0,
    headline: bool = True,
    data_dir: Path | None = None,
) -> list[ResultRow]:
    """Score one lane run in every match mode.

    Parameters
    ----------
    lane_run:
        A stored run; only the docs it predicted are scored.
    docs:
        The split's gold docs (a superset of the run's).
    decoder:
        Re-decode the run's word scores with these settings instead of using its spans.
    seed:
        Bootstrap seed.
    headline:
        Whether these rows are the lane's headline rows.
    data_dir:
        When given, a headline TAB row also gets TAB's official measures, computed by its
        own script from the fetched data there.

    Returns
    -------
    list[ResultRow]
        One row per match mode, word-level first.
    """
    by_id = {doc.id: doc for doc in docs}
    scored = [by_id[prediction.doc_id] for prediction in lane_run.predictions]
    spans = [_spans(doc, p, decoder) for doc, p in zip(scored, lane_run.predictions, strict=True)]
    probs, labels = _word_probs(scored, lane_run.predictions)
    rows = [
        _row(lane_run, scored, spans, mode, decoder, headline, seed, probs, labels)
        for mode in MODES
    ]
    if data_dir is None or lane_run.dataset != "tab" or not headline:
        return rows
    masked = [
        prediction.model_copy(update={"spans": tuple(doc_spans)})
        for prediction, doc_spans in zip(lane_run.predictions, spans, strict=True)
    ]
    official = tab_official_scores(masked, data_dir, lane_run.split)
    return [rows[0].model_copy(update={"tab_official": official}), *rows[1:]]


def _spans(doc: Doc, prediction: Prediction, decoder: DecodeParams | None) -> Sequence[Span]:
    if decoder is None or prediction.word_scores is None:
        return prediction.spans
    return decode(split_words(doc.text), prediction.word_scores, decoder)


def _word_probs(
    docs: Sequence[Doc], predictions: Sequence[Prediction]
) -> tuple[list[float], list[bool]]:
    """Every word's predicted probability and gold truth, for lanes that score words."""
    probs: list[float] = []
    labels: list[bool] = []
    for doc, prediction in zip(docs, predictions, strict=True):
        if prediction.word_scores is None:
            continue
        gold = covering_spans(split_words(doc.text), doc.gold)
        probs.extend(score.p_pii for score in prediction.word_scores)
        labels.extend(span is not None for span in gold)
    return probs, labels


def _row(
    lane_run: LaneRun,
    docs: Sequence[Doc],
    spans: Sequence[Sequence[Span]],
    mode: MatchMode,
    decoder: DecodeParams | None,
    headline: bool,
    seed: int,
    probs: list[float],
    labels: list[bool],
) -> ResultRow:
    counts = [doc_counts(doc, pred, mode) for doc, pred in zip(docs, spans, strict=True)]
    ## Curves describe the raw word scores, so they belong to the undecoded row only.
    curves = bool(probs) and decoder is None
    shown = lane_run.dataset in _STRINGS_PUBLISHABLE or lane_run.split == "dev"
    missed, false_alarms = top_errors(docs, spans) if shown else ([], [])
    return ResultRow(
        lane=lane_run.lane,
        decoder=describe(decoder) if decoder else None,
        headline=headline,
        dataset=lane_run.dataset,
        split=lane_run.split,
        mode=mode,
        n_docs=len(docs),
        scores=scores_from_counts(counts),
        f2_ci=bootstrap_ci(
            len(counts), lambda ids: scores_from_counts(counts[i] for i in ids).f2, seed=seed
        ),
        cost=cost_summary(lane_run.predictions, lane_run.wall_clock_s),
        ece=ece(probs, labels) if probs else None,
        brier=brier(probs, labels) if probs else None,
        gold_by_type=gold_hits_by(docs, spans, key=lambda span: span.label),
        gold_by_detail=gold_hits_by(docs, spans, key=lambda span: span.detail),
        gold_by_shape=gold_hits_by(
            docs,
            spans,
            key=lambda span: shape(lane_run.dataset, span.detail) if span.detail else None,
        ),
        predicted_by_type=predicted_hits_by_type(docs, spans),
        cleared_masked=cleared_hits(docs, spans) if any(d.cleared for d in docs) else None,
        failed=sum(p.failed for p in lane_run.predictions),
        dropped=sum(p.dropped for p in lane_run.predictions),
        per_doc=tuple(
            _doc_result(doc, p, c)
            for doc, p, c in zip(docs, lane_run.predictions, counts, strict=True)
        ),
        reliability=tuple(reliability_bins(probs, labels)) if curves else None,
        threshold_curve=tuple(threshold_curve(probs, labels)) if curves else None,
        top_missed=tuple(missed),
        top_false_alarms=tuple(false_alarms),
    )


def _doc_result(doc: Doc, prediction: Prediction, counts: DocCounts) -> DocResult:
    return DocResult(
        doc_id=doc.id,
        n_words=len(split_words(doc.text)),
        tp=counts.tp,
        fp=counts.fp,
        fn=counts.fn,
        cost_usd=prediction.usage.cost_usd,
        latency_s=prediction.usage.latency_s,
        input_tokens=prediction.usage.input_tokens,
        output_tokens=prediction.usage.output_tokens,
        failed=prediction.failed,
        dropped=prediction.dropped,
    )
