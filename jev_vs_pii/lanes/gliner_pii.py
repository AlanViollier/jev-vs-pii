"""NVIDIA GLiNER-PII, run locally: zero-shot span extraction for whatever labels it is given."""

from __future__ import annotations

import os
from collections.abc import Sequence

from jev_vs_pii.schema import Doc, LaneInfo, Prediction, Span
from jev_vs_pii.taxonomy import Coarse
from jev_vs_pii.words import split_words, word_scores_from

MODEL = "nvidia/gliner-pii"
_REVISION = "bd23e8ef4425fd04e34c5204ab49ffaa706eae79"
## The model card's default decision threshold.
_THRESHOLD = 0.5
## Low enough that the word scores keep near-misses for decoder tuning and calibration.
_SCORE_FLOOR = 0.05
## Long docs go in windows that fit GLiNER's own token limit, overlapping by this many words.
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
        ## GLiNER cuts anything past `max_len` of its own tokens (punctuation counts) silently.
        self._max_tokens: int = self._model.config.max_len
        self._split = self._model.data_processor.words_splitter
        self.info = LaneInfo(id="gliner_pii", family="ner", model=MODEL)
        ## One throwaway pass so per-doc latency doesn't include warm-up.
        self._model.predict_entities("Warm up with Jane Roe.", list(LABELS))

    async def predict(self, doc: Doc) -> Prediction:
        """Run each word window, map its entities back to doc offsets, keep the best per range."""
        words = split_words(doc.text)
        ## A word's tokens include the punctuation before it, which `split_words` trims off.
        starts = [0, *(word.end for word in words[:-1])]
        sizes = [
            len(list(self._split(doc.text[start : word.end])))
            for start, word in zip(starts, words, strict=True)
        ]
        candidates: dict[tuple[int, int], Span] = {}
        for first, last in windows(sizes, self._max_tokens, _OVERLAP_WORDS):
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


def windows(sizes: Sequence[int], budget: int, overlap: int) -> list[tuple[int, int]]:
    """Half-open word ranges covering every word, each at most `budget` tokens.

    `sizes` is each word's token count. Each window starts `overlap` words before the
    previous one ended, and always moves forward by at least one word; a single word
    over budget gets a window of its own.
    """
    ranges: list[tuple[int, int]] = []
    start = 0
    while start < len(sizes):
        end, used = start, 0
        while end < len(sizes) and (end == start or used + sizes[end] <= budget):
            used += sizes[end]
            end += 1
        ranges.append((start, end))
        if end == len(sizes):
            break
        start = max(end - overlap, start + 1)
    return ranges
