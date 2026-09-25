"""Doc-level bootstrap intervals are reproducible, ordered, and collapse on a constant statistic."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from pii_bench.metrics.bootstrap import bootstrap_ci
from pii_bench.metrics.spans import DocCounts, scores_from_counts
from pii_bench.utils.stats import percentile

_COUNTS = [DocCounts(tp=i % 5, fp=i % 3, fn=(i * 7) % 4) for i in range(60)]


def _f2(doc_ids: Sequence[int]) -> float:
    return scores_from_counts(_COUNTS[i] for i in doc_ids).f2


def test_interval_brackets_the_point_estimate() -> None:
    low, high = bootstrap_ci(len(_COUNTS), _f2, n_resamples=300)
    assert low < _f2(range(len(_COUNTS))) < high


def test_same_seed_same_interval() -> None:
    assert bootstrap_ci(len(_COUNTS), _f2, n_resamples=200, seed=3) == bootstrap_ci(
        len(_COUNTS), _f2, n_resamples=200, seed=3
    )


def test_constant_statistic_has_zero_width() -> None:
    assert bootstrap_ci(10, lambda ids: 0.5, n_resamples=50) == (0.5, 0.5)


@pytest.mark.parametrize(
    ("values", "q", "expected"),
    [
        ([3.0, 1.0, 2.0], 50, 2.0),
        ([1.0, 2.0, 3.0, 4.0], 50, 2.5),
        ([10.0], 95, 10.0),
        ([0.0, 10.0], 95, 9.5),
    ],
)
def test_percentile_interpolates_like_numpy(values: list[float], q: float, expected: float) -> None:
    assert percentile(values, q) == pytest.approx(expected)
