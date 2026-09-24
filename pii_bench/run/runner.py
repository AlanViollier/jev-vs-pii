"""Run one lane over docs concurrently, reporting each prediction as it lands."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from pii_bench.lanes import Lane
from pii_bench.schema import Doc, Prediction

OnPrediction = Callable[[Lane, Doc, Prediction], None]


async def run_lane(
    lane: Lane,
    docs: Sequence[Doc],
    concurrency: int,
    on_prediction: OnPrediction | None = None,
) -> list[Prediction]:
    """Predict every doc with at most `concurrency` in flight.

    Parameters
    ----------
    lane:
        The lane under test.
    docs:
        Docs for this tier.
    concurrency:
        Max simultaneous `predict` calls.
    on_prediction:
        Called after each doc, e.g. by the live dashboard.

    Returns
    -------
    list[Prediction]
        In doc order. `BudgetExceeded` propagates; predictions made before it are
        already in the cache, so a rerun after raising the cap pays nothing twice.
    """
    raise NotImplementedError
