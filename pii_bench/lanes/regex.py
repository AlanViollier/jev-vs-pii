"""Format-driven patterns only: emails, phones, IPs, card and ID numbers, dates."""

from __future__ import annotations

from pii_bench.schema import Doc, LaneInfo, Prediction


class RegexLane:
    """Lane `regex`."""

    info: LaneInfo

    def __init__(self) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
