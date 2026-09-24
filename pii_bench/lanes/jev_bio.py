"""Jev, per word: is it PII, and does it continue the previous item? Output: word scores with joins."""

from __future__ import annotations

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams
from pii_bench.schema import Doc, LaneInfo, Prediction


class JevBioLane:
    """Lane `jev_bio`."""

    info: LaneInfo

    def __init__(self, client: DecisionsClient, decode: DecodeParams) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
