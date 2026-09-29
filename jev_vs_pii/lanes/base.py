"""What every lane looks like from the outside."""

from __future__ import annotations

from typing import Protocol

from jev_vs_pii.schema import Doc, LaneInfo, Prediction


class Lane(Protocol):
    """One standalone PII method: a doc in, spans (and word scores if it has them) out."""

    info: LaneInfo

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        ...
