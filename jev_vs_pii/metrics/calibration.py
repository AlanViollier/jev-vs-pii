"""How far a lane's confidence can be trusted: ECE, Brier, reliability bins."""

from __future__ import annotations

from collections.abc import Sequence

from jev_vs_pii.schema import ReliabilityBin


def ece(probs: Sequence[float], labels: Sequence[bool], n_bins: int = 10) -> float:
    """Expected calibration error over equal-width bins.

    Parameters
    ----------
    probs:
        Predicted probability of PII, one per word.
    labels:
        Gold truth per word.
    n_bins:
        Number of equal-width confidence bins.

    Returns
    -------
    float
        Count-weighted mean |confidence − accuracy|; 0 is perfectly calibrated.
    """
    bins = reliability_bins(probs, labels, n_bins)
    total = sum(b.count for b in bins)
    return sum(b.count * abs(b.mean_confidence - b.accuracy) for b in bins) / total


def brier(probs: Sequence[float], labels: Sequence[bool]) -> float:
    """Mean squared error between probability and outcome; 0 is perfect, 0.25 is a coin flip."""
    return sum((p - y) ** 2 for p, y in zip(probs, labels, strict=True)) / len(probs)


def reliability_bins(
    probs: Sequence[float], labels: Sequence[bool], n_bins: int = 10
) -> list[ReliabilityBin]:
    """Bins for the reliability diagram; empty bins are omitted.

    Bin i holds probabilities in [i/n, (i+1)/n); a probability of exactly 1 joins the last bin.
    `accuracy` is the share of the bin's words that really are PII.
    """
    members: list[list[tuple[float, bool]]] = [[] for _ in range(n_bins)]
    for prob, label in zip(probs, labels, strict=True):
        members[min(int(prob * n_bins), n_bins - 1)].append((prob, label))
    return [
        ReliabilityBin(
            low=i / n_bins,
            high=(i + 1) / n_bins,
            count=len(pairs),
            mean_confidence=sum(p for p, _ in pairs) / len(pairs),
            accuracy=sum(y for _, y in pairs) / len(pairs),
        )
        for i, pairs in enumerate(members)
        if pairs
    ]
