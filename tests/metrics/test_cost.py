"""Cost is normalised per 1k docs in exact decimals; latency percentiles come from per-doc time."""

from __future__ import annotations

from decimal import Decimal

from pii_bench.metrics.cost import cost_summary
from pii_bench.schema import Prediction, Usage


def _prediction(cost: str, calls: int, latency_s: float) -> Prediction:
    usage = Usage(calls=calls, cost_usd=Decimal(cost), latency_s=latency_s)
    return Prediction(doc_id="d", lane_id="l", spans=(), usage=usage)


def test_cost_summary_per_doc() -> None:
    predictions = [_prediction("0.0001", 1, 0.4), _prediction("0.0003", 2, 1.2)]
    summary = cost_summary(predictions, wall_clock_s=1.5)
    assert summary.usd_per_1k_docs == Decimal("0.2")
    assert summary.calls_per_doc == 1.5
    assert summary.latency_p50_s == 0.8
    assert summary.wall_clock_s == 1.5


def test_single_doc_run_has_its_own_latency_as_every_percentile() -> None:
    summary = cost_summary([_prediction("0", 0, 0.3)], wall_clock_s=0.3)
    assert (summary.latency_p50_s, summary.latency_p95_s) == (0.3, 0.3)
