"""GLiNER zero-shot NER, prompted with the coarse label names."""

from __future__ import annotations

from pii_bench.schema import Doc, LaneInfo, Prediction


class GlinerLane:
    """Lane `gliner`."""

    info: LaneInfo

    def __init__(self) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
