"""Jev, fixed chunks first, then words inside the chunks that say yes. Output: word scores."""

from __future__ import annotations

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams
from pii_bench.schema import Doc, LaneInfo, Prediction


class JevChunksLane:
    """Lane `jev_chunks`."""

    info: LaneInfo

    def __init__(self, client: DecisionsClient, decode: DecodeParams) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
