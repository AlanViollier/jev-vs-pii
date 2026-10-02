"""Jev as a decision model: the doc as state once per call, questions packed into as few calls as fit."""

from __future__ import annotations

import asyncio
import json

from jev_vs_pii.clients import DecisionsClient
from jev_vs_pii.lanes.designs import Answer, Question
from jev_vs_pii.schema import Doc, Usage
from jev_vs_pii.taxonomy import definition

## Calls of 64k tokens went through, one past that was refused: stay well under.
MAX_INPUT_TOKENS = 48_000
## Fewest JSON characters per billed token seen on large Jev calls was 2.48, so this over-counts.
_CHARS_PER_TOKEN = 2.4


class JevModel:
    """Model key `jev`: OpenRouter's Decisions API, packed calls run concurrently."""

    key = "jev"

    def __init__(self, client: DecisionsClient) -> None:
        self.model_id = client.model
        self._client = client

    async def answer(
        self, doc: Doc, questions: dict[str, Question]
    ) -> tuple[dict[str, Answer], Usage]:
        """Ask every question with the doc as state, in as few calls as `MAX_INPUT_TOKENS` allows."""
        state = state_for(doc)
        results = await asyncio.gather(
            *(self._client.ask(state, batch) for batch in batches(state, questions))
        )
        answers: dict[str, Answer] = {}
        for result in results:
            answers.update(result.answers)
        return answers, Usage.combine([result.usage for result in results])


def state_for(doc: Doc) -> str:
    """What Jev reads before any question: the PII brief, then the doc."""
    return f"{definition(doc)}\n\nText:\n{doc.text}"


def estimated_tokens(text: str) -> float:
    """An over-count of the tokens Jev bills for `text`, as JSON."""
    return len(text) / _CHARS_PER_TOKEN


def question_json(key: str, question: Question) -> str:
    """One question as it appears in the request body."""
    return json.dumps({key: question.model_dump()})


def batches(state: str, questions: dict[str, Question]) -> list[dict[str, Question]]:
    """Split questions into calls whose estimated size, state included, fits `MAX_INPUT_TOKENS`."""
    budget = MAX_INPUT_TOKENS * _CHARS_PER_TOKEN - len(json.dumps(state))
    calls: list[dict[str, Question]] = [{}]
    used = 0.0
    for key, question in questions.items():
        size = len(question_json(key, question))
        if calls[-1] and used + size > budget:
            calls.append({})
            used = 0.0
        calls[-1][key] = question
        used += size
    return calls if calls[0] else []
