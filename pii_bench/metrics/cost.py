"""Cost and latency of a lane run, normalised per document."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.schema import CostSummary, Prediction


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
    raise NotImplementedError
