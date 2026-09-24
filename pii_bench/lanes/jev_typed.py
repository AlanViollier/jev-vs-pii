"""Jev, one pick-one question per word over the coarse types plus not-PII. Output: typed word scores."""

from __future__ import annotations

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams
from pii_bench.schema import Doc, LaneInfo, Prediction


class JevTypedLane:
    """Lane `jev_typed`."""

    info: LaneInfo

    def __init__(self, client: DecisionsClient, decode: DecodeParams) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
