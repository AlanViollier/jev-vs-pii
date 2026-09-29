"""OpenAI Privacy Filter, run locally: a token classifier with BIOES tags over 8 PII categories.

Logits come from the Hugging Face port (runs on Apple GPUs); spans come from OpenAI's own
constrained Viterbi decoder in its `opf` package, at the shipped default operating point.
"""

from __future__ import annotations

import os

from pii_bench.schema import Doc, LaneInfo, Prediction, Span
from pii_bench.taxonomy import Coarse
from pii_bench.words import split_words, word_scores_from

MODEL = "openai/privacy-filter"
_REVISION = "7ffa9a043d54d1be65afb281eddf0ffbe629385b"
_COARSE: dict[str, Coarse] = {
    "private_person": "PERSON",
    "private_address": "LOCATION",
    "private_email": "CONTACT",
    "private_phone": "CONTACT",
    "private_url": "CONTACT",
    "private_date": "DATETIME",
    "account_number": "ID",
    "secret": "ID",
}


class PrivacyFilterLane:
    """Lane `privacy_filter`: its own argmax spans, plus P(not O) per word for decoders and calibration."""

    def __init__(self) -> None:
        ## Loaded here, not at import: torch and the weights come with the optional NER extra.
        ## The tokenizers thread pool aborts noisily at interpreter exit once torch has run.
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        import torch
        from opf._core.decoding import ViterbiCRFDecoder
        from opf._core.sequence_labeling import build_label_info
        from transformers import AutoModelForTokenClassification, AutoTokenizer

        self._torch = torch
        self._device = "mps" if torch.backends.mps.is_available() else "cpu"
        self._tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=_REVISION)
        self._model = (
            AutoModelForTokenClassification.from_pretrained(MODEL, revision=_REVISION)
            .to(self._device)
            .eval()
        )
        self._labels: dict[int, str] = self._model.config.id2label
        class_names = [self._labels[i] for i in range(len(self._labels))]
        self._decoder = ViterbiCRFDecoder(label_info=build_label_info(class_names))
        self.info = LaneInfo(id="privacy_filter", family="ner", model=MODEL)
        ## One throwaway pass so per-doc latency doesn't include kernel warm-up.
        self._classify("Warm up with Jane Roe.")

    async def predict(self, doc: Doc) -> Prediction:
        """Classify every token in one pass; the runner times it as it blocks."""
        tokens = self._classify(doc.text)
        words = split_words(doc.text)
        scored = [Span(start=start, end=end, score=p) for start, end, _, p in tokens]
        return Prediction(
            doc_id=doc.id,
            lane_id=self.info.id,
            spans=tuple(bioes_spans(doc.text, tokens)),
            word_scores=word_scores_from(words, scored),
        )

    def _classify(self, text: str) -> list[tuple[int, int, str, float]]:
        """(start, end, decoded tag, P(not O)) for every non-empty token."""
        encoded = self._tokenizer(text, return_offsets_mapping=True, return_tensors="pt")
        offsets = encoded.pop("offset_mapping")[0].tolist()
        with self._torch.no_grad():
            logits = self._model(**encoded.to(self._device)).logits[0]
        log_probs = logits.float().log_softmax(-1).cpu()
        tags = self._decoder.decode(log_probs)
        outside = next(i for i, label in self._labels.items() if label == "O")
        return [
            (start, end, self._labels[tags[i]], 1.0 - float(log_probs[i, outside].exp()))
            for i, (start, end) in enumerate(offsets)
            if end > start
        ]


def bioes_spans(text: str, tokens: list[tuple[int, int, str, float]]) -> list[Span]:
    """Merge tagged tokens into spans: B/I/E of one category join, S stands alone, O breaks.

    A tag that doesn't continue the open span (a stray I or E) starts a new one, so a
    sloppy tag sequence still yields spans instead of being dropped. Tokens carry their
    leading space, so each span is trimmed to its first and last non-space character.

    Parameters
    ----------
    text:
        The doc text the token offsets point into.
    tokens:
        (start, end, tag, p_pii) per token in text order; tags look like `B-private_person`.

    Returns
    -------
    list[Span]
        Coarse-labelled spans scored by the mean p_pii of their tokens.
    """
    spans: list[Span] = []
    current: list[tuple[int, int, float]] = []
    category = ""

    def close() -> None:
        start, end = (current[0][0], current[-1][1]) if current else (0, 0)
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if start < end:
            spans.append(
                Span(
                    start=start,
                    end=end,
                    label=_COARSE.get(category, "OTHER"),
                    score=sum(p for _, _, p in current) / len(current),
                )
            )
        current.clear()

    for start, end, tag, p in tokens:
        if tag == "O":
            close()
            continue
        prefix, _, name = tag.partition("-")
        if prefix in ("B", "S") or name != category or not current:
            close()
            category = name
        current.append((start, end, p))
        if prefix in ("E", "S"):
            close()
    close()
    return spans
