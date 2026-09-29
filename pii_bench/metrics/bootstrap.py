"""Confidence intervals by resampling whole documents."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

from pii_bench.metrics.spans import DocCounts, scores_from_counts
from pii_bench.utils.stats import percentile


def bootstrap_ci(
    n_docs: int,
    statistic: Callable[[Sequence[int]], float],
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Percentile interval for `statistic` over doc-level resamples.

    Parameters
    ----------
    n_docs:
        Number of documents in the scored set.
    statistic:
        Computes the metric from a list of doc indices (with repeats).
    n_resamples:
        Resamples to draw.
    seed:
        RNG seed; same seed, same interval.
    alpha:
        0.05 gives a 95% interval.

    Returns
    -------
    tuple[float, float]
        Lower and upper bound.
    """
    rng = random.Random(seed)  # nosec B311: reproducible resampling, not security
    doc_ids = range(n_docs)
    stats = [statistic(rng.choices(doc_ids, k=n_docs)) for _ in range(n_resamples)]
    return percentile(stats, 100 * alpha / 2), percentile(stats, 100 * (1 - alpha / 2))


def paired_f2_diff(
    a: Sequence[DocCounts],
    b: Sequence[DocCounts],
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """F2 of `a` minus F2 of `b` on the same docs, with a paired percentile interval.

    Resampling the same doc indices for both lanes cancels out how hard each doc is, so
    the interval is much tighter than comparing two separate intervals.

    Parameters
    ----------
    a, b:
        Per-doc counts of two lanes, aligned doc for doc.
    n_resamples:
        Resamples to draw.
    seed:
        RNG seed.
    alpha:
        0.05 gives a 95% interval.

    Returns
    -------
    tuple[float, float, float]
        The observed difference, then the interval's lower and upper bound. An interval
        that excludes 0 means the gap is not resampling noise.
    """
    if len(a) != len(b):
        raise ValueError(f"paired comparison needs the same docs: {len(a)} vs {len(b)}")

    def diff(ids: Sequence[int]) -> float:
        return scores_from_counts(a[i] for i in ids).f2 - scores_from_counts(b[i] for i in ids).f2

    low, high = bootstrap_ci(len(a), diff, n_resamples, seed, alpha)
    return diff(range(len(a))), low, high
