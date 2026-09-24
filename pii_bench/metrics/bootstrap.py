"""Confidence intervals by resampling whole documents."""

from __future__ import annotations

from collections.abc import Callable, Sequence


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
    raise NotImplementedError
