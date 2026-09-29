"""Jev through OpenRouter's Decisions API: one text, many typed questions, probabilities back."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ValidationError

from pii_bench.clients.budget import Ledger
from pii_bench.clients.cache import ResponseCache
from pii_bench.clients.http import paid_post
from pii_bench.exceptions import ProviderError
from pii_bench.schema import Usage

DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"

## Jev 1.13 on OpenRouter, Sep 2026: $0.042 per M input tokens, output free.
_INPUT_USD_PER_TOKEN = Decimal("0.042") / 1_000_000


class Noul(BaseModel):
    """Yes/no question; the answer is the probability of yes."""

    type: Literal["noul"] = "noul"
    instructions: str


class Choice(BaseModel):
    """Pick-one question; `criteria` maps each option to its description."""

    type: Literal["choice"] = "choice"
    instructions: str
    criteria: dict[str, str]


class NoulAnswer(BaseModel):
    """Probability that the answer is yes."""

    type: Literal["noul"]
    noul: float


class ChoiceAnswer(BaseModel):
    """Picked option, the full distribution, and the model's confidence."""

    type: Literal["choice"]
    choice: str
    probabilities: dict[str, float]
    confidence: float


class _Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    cost: float


class _Body(BaseModel):
    answers: dict[str, NoulAnswer | ChoiceAnswer]
    usage: _Usage


class DecisionResult(BaseModel):
    """Answers keyed like the questions, plus what the call cost."""

    answers: dict[str, NoulAnswer | ChoiceAnswer]
    usage: Usage


class DecisionsClient:
    """Async client for the Decisions API; every call is budget-checked and cached."""

    def __init__(
        self,
        api_key: str,
        model: str,
        ledger: Ledger,
        cache: ResponseCache,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._model = model
        self._ledger = ledger
        self._cache = cache
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"}, timeout=120, transport=transport
        )

    @property
    def model(self) -> str:
        """The Jev model every call goes to."""
        return self._model

    async def ask(self, state: str, questions: dict[str, Noul | Choice]) -> DecisionResult:
        """Ask every question about `state` in one call.

        Parameters
        ----------
        state:
            The text the questions are about.
        questions:
            Question key → question. Keys come back unchanged in `answers`.

        Returns
        -------
        DecisionResult
            Raises `BudgetExceeded` before the call if it could pass the cap,
            `ProviderError` if the API errors or the answer doesn't parse. A cache hit
            reports the original cost and latency: they describe the method, not this run.
        """
        payload = {
            "model": self._model,
            "state": state,
            "questions": {key: question.model_dump() for key, question in questions.items()},
        }
        ## A token is at least one byte, so the byte count bounds the input tokens.
        estimate = len(json.dumps(payload).encode()) * _INPUT_USD_PER_TOKEN
        response, hit = await self._cache.get_or_call(
            {"url": DECISIONS_URL, **payload},
            lambda: paid_post(self._http, DECISIONS_URL, payload, self._ledger, estimate, _cost),
        )
        body = _parse(response.body)
        return DecisionResult(
            answers=body.answers,
            usage=Usage(
                calls=1,
                cache_hits=int(hit),
                input_tokens=body.usage.input_tokens,
                output_tokens=body.usage.output_tokens,
                cost_usd=Decimal(str(body.usage.cost)),
                latency_s=response.latency_s,
            ),
        )


def _cost(body: dict[str, Any]) -> Decimal:
    return Decimal(str(_parse(body).usage.cost))


def _parse(body: dict[str, Any]) -> _Body:
    """Validate a response body; anything unexpected is the provider's error, not ours."""
    try:
        return _Body.model_validate(body)
    except ValidationError as error:
        raise ProviderError(f"unexpected Decisions API answer: {error}") from error
