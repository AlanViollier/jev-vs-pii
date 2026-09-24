"""Span precision / recall / F1 / F2, exact or overlap match, typed or not."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.schema import MatchMode, Span, SpanScores


def score_spans(
    gold: Sequence[Sequence[Span]],
    pred: Sequence[Sequence[Span]],
    mode: MatchMode,
    typed: bool = False,
) -> SpanScores:
    """Score predicted spans against gold, micro-averaged over docs.

    Parameters
    ----------
    gold:
        Gold spans per doc.
    pred:
        Predicted spans per doc, same doc order.
    mode:
        `exact` needs identical offsets; `overlap` counts any shared character.
    typed:
        When true a match also needs the same coarse label.

    Returns
    -------
    SpanScores
        Counts plus P / R / F1 / F2 (F2 weights recall: a leak costs more than an over-mask).
    """
    raise NotImplementedError
