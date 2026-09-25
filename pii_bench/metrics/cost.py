"""Cost and latency of a lane run, normalised per document."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from pii_bench.schema import CostSummary, Prediction
from pii_bench.utils.stats import percentile


def cost_summary(predictions: Sequence[Prediction], wall_clock_s: float) -> CostSummary:
    """Summarise what a run cost.

    Parameters
    ----------
    predictions:
        Every prediction in the run.
    wall_clock_s:
        Real elapsed time of the run, concurrency included.

    Returns
    -------
    CostSummary
        $/1k docs, calls/doc, per-doc latency p50/p95, wall-clock.
    """
    n_docs = len(predictions)
    latencies = [p.usage.latency_s for p in predictions]
    return CostSummary(
        usd_per_1k_docs=sum((p.usage.cost_usd for p in predictions), Decimal(0)) * 1000 / n_docs,
        calls_per_doc=sum(p.usage.calls for p in predictions) / n_docs,
        latency_p50_s=percentile(latencies, 50),
        latency_p95_s=percentile(latencies, 95),
        wall_clock_s=wall_clock_s,
    )
