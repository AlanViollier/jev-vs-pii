"""A decision model asked a design's questions about every word of a doc. Lane ids: `decision_<design>:<model>`."""

from __future__ import annotations

from typing import Protocol

from jev_vs_pii.decode import DecodeParams, Threshold, decode
from jev_vs_pii.lanes.designs import Answer, Design, Question
from jev_vs_pii.schema import Doc, LaneInfo, Prediction, Usage
from jev_vs_pii.words import split_words


class DecisionModel(Protocol):
    """Answers typed questions about a doc. How the doc and questions fit its context is its own business."""

    key: str
    model_id: str

    async def answer(
        self, doc: Doc, questions: dict[str, Question]
    ) -> tuple[dict[str, Answer], Usage]:
        """An answer for every question, and what getting them cost."""
        ...


class DecisionLane:
    """Lane `decision_<design>:<model key>`: every word scored from the model's answers, then decoded to spans."""

    def __init__(
        self, model: DecisionModel, design: Design, decoder: DecodeParams | None = None
    ) -> None:
        self.info = LaneInfo(
            id=f"decision_{design.name}:{model.key}", family="decision", model=model.model_id
        )
        self._model = model
        self._design = design
        self._decoder: DecodeParams = decoder or Threshold()

    async def predict(self, doc: Doc) -> Prediction:
        """Score every word, then decode spans with this lane's decoder (threshold 0.5 unless tuned)."""
        words = split_words(doc.text)
        questions: dict[str, Question] = {}
        for i in range(len(words)):
            questions.update(self._design.ask(doc, words, i))
        answers, usage = await self._model.answer(doc, questions)
        scores = tuple(self._design.score(answers, words, i) for i in range(len(words)))
        return Prediction(
            doc_id=doc.id,
            lane_id=self.info.id,
            spans=tuple(decode(words, scores, self._decoder)),
            word_scores=scores,
            usage=usage,
        )
