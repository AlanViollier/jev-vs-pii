"""Jev asked about every word of a doc, in as few calls as its context allows. Lane ids: `jev_<design>`."""

from __future__ import annotations

import asyncio
import itertools

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams, Threshold, decode
from pii_bench.lanes.jev_designs import Answer, JevDesign, Question
from pii_bench.schema import Doc, LaneInfo, Prediction, Usage
from pii_bench.taxonomy import definition
from pii_bench.words import split_words

## Jev reads 32k tokens; a question with its context runs ~30, the longest TAB doc ~3k.
MAX_QUESTIONS_PER_CALL = 400


class JevLane:
    """Lane `jev_<design>`: every question batched into calls that share the doc as state, run concurrently."""

    def __init__(
        self, client: DecisionsClient, design: JevDesign, decoder: DecodeParams | None = None
    ) -> None:
        self.info = LaneInfo(id=f"jev_{design.name}", family="jev", model=client.model)
        self._client = client
        self._design = design
        self._decoder: DecodeParams = decoder or Threshold()

    async def predict(self, doc: Doc) -> Prediction:
        """Score every word, then decode spans with this lane's decoder (threshold 0.5 unless tuned)."""
        words = split_words(doc.text)
        questions: dict[str, Question] = {}
        for i in range(len(words)):
            questions.update(self._design.ask(doc.text, words, i))
        state = f"{definition(doc)}\n\nText:\n{doc.text}"
        results = await asyncio.gather(
            *(self._client.ask(state, dict(batch)) for batch in _batches(questions))
        )
        answers: dict[str, Answer] = {}
        for result in results:
            answers.update(result.answers)
        scores = tuple(self._design.score(answers, i) for i in range(len(words)))
        return Prediction(
            doc_id=doc.id,
            lane_id=self.info.id,
            spans=tuple(decode(words, scores, self._decoder)),
            word_scores=scores,
            usage=Usage.combine([result.usage for result in results]),
        )


def _batches(questions: dict[str, Question]) -> list[tuple[tuple[str, Question], ...]]:
    return list(itertools.batched(questions.items(), MAX_QUESTIONS_PER_CALL))
