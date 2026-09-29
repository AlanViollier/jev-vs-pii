"""Score a stored lane run into result rows: accuracy with CIs, calibration, per-type recall, cost."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from pii_bench.decode import DecodeParams, decode, describe
from pii_bench.metrics.bootstrap import bootstrap_ci
from pii_bench.metrics.calibration import brier, ece
from pii_bench.metrics.cost import cost_summary
from pii_bench.metrics.spans import doc_counts, recall_by_type, scores_from_counts
from pii_bench.schema import Doc, LaneInfo, LaneRun, MatchMode, Prediction, ResultRow, Span
from pii_bench.words import covering_spans, split_words

MODES: tuple[MatchMode, ...] = ("word", "exact")


def score_lane_run(
    lane_run: LaneRun,
    docs: Sequence[Doc],
    decoder: DecodeParams | None = None,
    seed: int = 0,
    headline: bool = True,
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

    Returns
    -------
    list[ResultRow]
        One row per match mode, word-level first.
    """
    by_id = {doc.id: doc for doc in docs}
    scored = [by_id[prediction.doc_id] for prediction in lane_run.predictions]
    spans = [_spans(doc, p, decoder) for doc, p in zip(scored, lane_run.predictions, strict=True)]
    probs, labels = _word_probs(scored, lane_run.predictions)
    return [
        _row(lane_run, scored, spans, mode, decoder, headline, seed, probs, labels)
        for mode in MODES
    ]


def human_lane_run(docs: Sequence[Doc]) -> LaneRun | None:
    """TAB's second annotator as a lane: the agreement ceiling any method is read against.

    Parameters
    ----------
    docs:
        Gold docs; only those with a second annotator are kept.

    Returns
    -------
    LaneRun | None
        None when no doc has a second annotator (ai4privacy).
    """
    annotated = [doc for doc in docs if doc.other_annotators]
    if not annotated:
        return None
    first = annotated[0]
    return LaneRun(
        run_id="human",
        lane=LaneInfo(id="human", family="human"),
        dataset=first.dataset,
        split=first.split,
        tier="full",
        started_at=datetime.now(),
        wall_clock_s=0.0,
        predictions=tuple(
            Prediction(doc_id=doc.id, lane_id="human", spans=doc.other_annotators[0])
            for doc in annotated
        ),
    )


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
        recall_by_type=recall_by_type(docs, spans),
        failed=sum(p.failed for p in lane_run.predictions),
        dropped=sum(p.dropped for p in lane_run.predictions),
    )
