"""Jev, bisection: ask about halves while the answer is yes, one call per level. Output: word scores."""

from __future__ import annotations

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams
from pii_bench.schema import Doc, LaneInfo, Prediction


class JevTreeLane:
    """Lane `jev_tree`."""

    info: LaneInfo

    def __init__(self, client: DecisionsClient, decode: DecodeParams) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
