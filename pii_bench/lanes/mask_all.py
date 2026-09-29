"""The floor: mask the whole doc. Any lane has to beat this to have learned anything."""

from __future__ import annotations

from pii_bench.schema import Doc, LaneInfo, Prediction, Span


class MaskAllLane:
    """Lane `mask_all`: one span over the entire text."""

    info = LaneInfo(id="mask_all", family="baseline")

    async def predict(self, doc: Doc) -> Prediction:
        """Return one span covering `doc.text`."""
        return Prediction(
            doc_id=doc.id, lane_id=self.info.id, spans=(Span(start=0, end=len(doc.text)),)
        )
