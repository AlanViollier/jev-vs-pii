"""NVIDIA GLiNER-PII, run locally: zero-shot span extraction for whatever labels it is given."""

from __future__ import annotations

import os

from pii_bench.schema import Doc, LaneInfo, Prediction, Span
from pii_bench.taxonomy import Coarse
from pii_bench.words import split_words, word_scores_from

MODEL = "nvidia/gliner-pii"
_REVISION = "bd23e8ef4425fd04e34c5204ab49ffaa706eae79"
## The model card's default decision threshold.
_THRESHOLD = 0.5
## Low enough that the word scores keep near-misses for decoder tuning and calibration.
_SCORE_FLOOR = 0.05
## GLiNER reads ~384 tokens; long docs go in overlapping word windows.
_WINDOW_WORDS = 250
_OVERLAP_WORDS = 50
LABELS: dict[str, Coarse] = {
    "person": "PERSON",
    "email address": "CONTACT",
    "phone number": "CONTACT",
    "username": "CONTACT",
    "ip address": "CONTACT",
    "url": "CONTACT",
    "street address": "LOCATION",
    "city": "LOCATION",
    "country": "LOCATION",
    "postal code": "LOCATION",
    "date": "DATETIME",
    "time": "DATETIME",
    "date of birth": "DATETIME",
    "identification number": "ID",
    "account number": "ID",
    "credit card number": "ID",
    "social security number": "ID",
    "password": "ID",
    "organization": "OTHER",
    "occupation": "OTHER",
    "age": "OTHER",
    "gender": "OTHER",
    "nationality": "OTHER",
}


class GlinerPiiLane:
    """Lane `gliner_pii`: spans above the card's threshold, word scores from every candidate."""

    def __init__(self) -> None:
        ## Loaded here, not at import: torch and the weights come with the optional NER extra.
        ## The tokenizers thread pool aborts noisily at interpreter exit once torch has run.
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        from gliner import GLiNER

        self._model = GLiNER.from_pretrained(MODEL, revision=_REVISION)
        self.info = LaneInfo(id="gliner_pii", family="ner", model=MODEL)
        ## One throwaway pass so per-doc latency doesn't include warm-up.
        self._model.predict_entities("Warm up with Jane Roe.", list(LABELS))

    async def predict(self, doc: Doc) -> Prediction:
        """Run each word window, map its entities back to doc offsets, keep the best per range."""
        words = split_words(doc.text)
        candidates: dict[tuple[int, int], Span] = {}
        for first, last in windows(len(words), _WINDOW_WORDS, _OVERLAP_WORDS):
            offset = words[first].start
            chunk = doc.text[offset : words[last - 1].end]
            for entity in self._model.predict_entities(chunk, list(LABELS), threshold=_SCORE_FLOOR):
                span = Span(
                    start=offset + entity["start"],
                    end=offset + entity["end"],
                    label=LABELS.get(entity["label"], "OTHER"),
                    score=min(max(float(entity["score"]), 0.0), 1.0),
                )
                key = (span.start, span.end)
                if key not in candidates or (span.score or 0) > (candidates[key].score or 0):
                    candidates[key] = span
        found = sorted(candidates.values(), key=lambda span: (span.start, span.end))
        return Prediction(
            doc_id=doc.id,
            lane_id=self.info.id,
            spans=tuple(span for span in found if (span.score or 0) >= _THRESHOLD),
            word_scores=word_scores_from(words, found),
        )


def windows(n_words: int, size: int, overlap: int) -> list[tuple[int, int]]:
    """Half-open word ranges of `size` covering `n_words`, each overlapping the last by `overlap`."""
    if n_words == 0:
        return []
    step = size - overlap
    return [
        (start, min(start + size, n_words)) for start in range(0, max(n_words - overlap, 1), step)
    ]
