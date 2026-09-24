"""Live terminal dashboard while lanes run (ember-CLI): progress, running F2, spend, current doc."""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from types import TracebackType

from pii_bench.lanes import Lane
from pii_bench.schema import Doc, Prediction


class LiveDashboard:
    """Context manager around `rich.live.Live`; feed it through `on_prediction`."""

    def __init__(self, lanes: Sequence[Lane], n_docs: int, budget_cap_usd: Decimal) -> None:
        raise NotImplementedError

    def __enter__(self) -> LiveDashboard:
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    def on_prediction(self, lane: Lane, doc: Doc, prediction: Prediction) -> None:
        """Update the lane's progress, running recall/F2 and spend; show the doc with hits, misses, false alarms."""
        raise NotImplementedError
