"""Microsoft Presidio's analyzer out of the box: default English recognizers on spaCy `en_core_web_lg`."""

from __future__ import annotations

from jev_vs_pii.schema import Doc, LaneInfo, Prediction, Span
from jev_vs_pii.taxonomy import Coarse

## Presidio's default English entity types; anything else it returns is OTHER.
_COARSE: dict[str, Coarse] = {
    "PERSON": "PERSON",
    "LOCATION": "LOCATION",
    "EMAIL_ADDRESS": "CONTACT",
    "PHONE_NUMBER": "CONTACT",
    "IP_ADDRESS": "CONTACT",
    "URL": "CONTACT",
    "CREDIT_CARD": "ID",
    "CRYPTO": "ID",
    "IBAN_CODE": "ID",
    "US_BANK_NUMBER": "ID",
    "US_DRIVER_LICENSE": "ID",
    "US_ITIN": "ID",
    "US_PASSPORT": "ID",
    "US_SSN": "ID",
    "UK_NHS": "ID",
    "MEDICAL_LICENSE": "ID",
    "DATE_TIME": "DATETIME",
}


class PresidioLane:
    """Lane `presidio`: every result Presidio returns at its default settings, with its score."""

    def __init__(self) -> None:
        ## Loaded here, not at import: the NER extra (spaCy model, ~600 MB) is optional.
        from presidio_analyzer import AnalyzerEngine

        self._analyzer = AnalyzerEngine()
        self.info = LaneInfo(id="presidio", family="ner", model="spacy/en_core_web_lg")

    async def predict(self, doc: Doc) -> Prediction:
        """Analyze `doc` synchronously; CPU-bound, so the runner times it as it blocks."""
        results = self._analyzer.analyze(text=doc.text, language="en")
        spans = sorted(
            (
                Span(
                    start=result.start,
                    end=result.end,
                    label=_COARSE.get(result.entity_type, "OTHER"),
                    score=min(max(result.score, 0.0), 1.0),
                )
                for result in results
                if result.end > result.start
            ),
            key=lambda span: (span.start, span.end),
        )
        return Prediction(doc_id=doc.id, lane_id=self.info.id, spans=tuple(spans))
