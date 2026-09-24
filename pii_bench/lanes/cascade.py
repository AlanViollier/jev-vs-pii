"""Regex for format types, Jev scores every word, the unsure band goes to an LLM. Experiment, not headline."""

from __future__ import annotations

from pii_bench.lanes.base import Lane
from pii_bench.schema import Doc, LaneInfo, Prediction


class CascadeLane:
    """Lane `cascade:<model>`."""

    info: LaneInfo

    def __init__(
        self, rules: Lane, scorer: Lane, escalate: Lane, band: tuple[float, float]
    ) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`, escalating only words whose score falls inside `band`."""
        raise NotImplementedError
