"""Run one lane over docs concurrently, reporting each prediction as it lands."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable, Sequence

from jev_vs_pii.lanes import Lane
from jev_vs_pii.schema import Doc, Prediction

OnPrediction = Callable[[Lane, Doc, Prediction], None]


async def run_lane(
    lane: Lane,
    docs: Sequence[Doc],
    concurrency: int,
    on_prediction: OnPrediction | None = None,
) -> list[Prediction]:
    """Predict every doc with at most `concurrency` in flight.

    Lanes that make no remote call are timed here; remote lanes report their calls' own
    latency, which a cache hit replays, so a rerun still describes the method.

    Parameters
    ----------
    lane:
        The lane under test.
    docs:
        Docs for this tier.
    concurrency:
        Max simultaneous `predict` calls.
    on_prediction:
        Called after each doc, e.g. to advance a progress bar.

    Returns
    -------
    list[Prediction]
        In doc order. `BudgetExceeded` and `ProviderError` propagate; predictions made
        before them are already in the cache, so a rerun pays nothing twice.
    """
    slots = asyncio.Semaphore(concurrency)

    async def predict(doc: Doc) -> Prediction:
        async with slots:
            started = time.perf_counter()
            prediction = await lane.predict(doc)
            if prediction.usage.calls == 0:
                usage = prediction.usage.model_copy(
                    update={"latency_s": time.perf_counter() - started}
                )
                prediction = prediction.model_copy(update={"usage": usage})
        if on_prediction is not None:
            on_prediction(lane, doc, prediction)
        return prediction

    return list(await asyncio.gather(*(predict(doc) for doc in docs)))
