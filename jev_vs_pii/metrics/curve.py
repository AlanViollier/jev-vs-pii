"""Precision and recall as the cutoff on per-word scores moves: the trade-off behind a decoder choice."""

from __future__ import annotations

from collections.abc import Sequence

from jev_vs_pii.metrics.spans import DocCounts, scores_from_counts
from jev_vs_pii.schema import CurvePoint

CUTOFFS = tuple(round(0.05 * step, 2) for step in range(1, 20))


def threshold_curve(
    probs: Sequence[float], labels: Sequence[bool], cutoffs: Sequence[float] = CUTOFFS
) -> list[CurvePoint]:
    """Word-level P / R / F2 at each cutoff, pooled over every word of the run.

    Parameters
    ----------
    probs:
        Each word's probability of being PII.
    labels:
        Each word's gold truth.
    cutoffs:
        Where to evaluate; a word is masked when its probability is at or above the cutoff.

    Returns
    -------
    list[CurvePoint]
        One point per cutoff, in order.
    """
    points = []
    for cutoff in cutoffs:
        tp = sum(p >= cutoff and y for p, y in zip(probs, labels, strict=True))
        fp = sum(p >= cutoff and not y for p, y in zip(probs, labels, strict=True))
        fn = sum(p < cutoff and y for p, y in zip(probs, labels, strict=True))
        scores = scores_from_counts([DocCounts(tp=tp, fp=fp, fn=fn)])
        points.append(
            CurvePoint(
                cutoff=cutoff, precision=scores.precision, recall=scores.recall, f2=scores.f2
            )
        )
    return points
