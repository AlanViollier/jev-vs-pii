"""Small statistics helpers the standard library lacks on Python 3.12."""

from __future__ import annotations

from collections.abc import Sequence


def percentile(values: Sequence[float], q: float) -> float:
    """Linearly interpolated percentile, the same rule as numpy's default.

    Parameters
    ----------
    values:
        At least one value, any order.
    q:
        Percentile in [0, 100].

    Returns
    -------
    float
        The interpolated value; a single value is its own every percentile.
    """
    ordered = sorted(values)
    position = (len(ordered) - 1) * q / 100
    below = int(position)
    above = min(below + 1, len(ordered) - 1)
    return ordered[below] + (ordered[above] - ordered[below]) * (position - below)
