"""Jev asked about every word of a doc, in as few calls as its context allows. Lane ids: `jev_<design>`."""

from __future__ import annotations

import asyncio
import json

from pii_bench.clients import DecisionsClient
from pii_bench.decode import DecodeParams, Threshold, decode
from pii_bench.lanes.jev_designs import Answer, JevDesign, Question
from pii_bench.schema import Doc, LaneInfo, Prediction, Usage
from pii_bench.taxonomy import definition
from pii_bench.words import split_words

## Calls of 64k tokens went through, one past that was refused: stay well under.
MAX_INPUT_TOKENS = 48_000
## Fewest JSON characters per billed token seen on large Jev calls was 2.48, so this over-counts.
_CHARS_PER_TOKEN = 2.4


class JevLane:
    """Lane `jev_<design>`: questions batched into as few calls as fit, each with the doc as state, run concurrently."""

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
            questions.update(self._design.ask(doc, words, i))
        state = f"{definition(doc)}\n\nText:\n{doc.text}"
        results = await asyncio.gather(
            *(self._client.ask(state, batch) for batch in _batches(state, questions))
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


def _batches(state: str, questions: dict[str, Question]) -> list[dict[str, Question]]:
    """Split questions into calls whose estimated size, state included, fits `MAX_INPUT_TOKENS`."""
    budget = MAX_INPUT_TOKENS * _CHARS_PER_TOKEN - len(json.dumps(state))
    batches: list[dict[str, Question]] = [{}]
    used = 0.0
    for key, question in questions.items():
        size = len(json.dumps({key: question.model_dump()}))
        if batches[-1] and used + size > budget:
            batches.append({})
            used = 0.0
        batches[-1][key] = question
        used += size
    return batches if batches[0] else []
