"""Microsoft Presidio's analyzer with its default English recognizers."""

from __future__ import annotations

from pii_bench.schema import Doc, LaneInfo, Prediction


class PresidioLane:
    """Lane `presidio`."""

    info: LaneInfo

    def __init__(self) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
