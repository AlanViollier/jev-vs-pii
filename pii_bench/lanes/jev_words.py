"""Jev, one yes/no question per word, all words in one call. Output: word scores."""

from __future__ import annotations

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams
from pii_bench.schema import Doc, LaneInfo, Prediction


class JevWordsLane:
    """Lane `jev_words`."""

    info: LaneInfo

    def __init__(self, client: DecisionsClient, decode: DecodeParams) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
