"""Jev through OpenRouter's Decisions API: one text, many typed questions, probabilities back."""

from __future__ import annotations

import json
import time
from decimal import Decimal
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from pii_bench.clients.budget import Ledger
from pii_bench.clients.cache import CachedResponse, ResponseCache
from pii_bench.exceptions import ProviderError
from pii_bench.schema import Usage

DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"

## Jev 1.13 on OpenRouter, Sep 2026: $0.042 per M input tokens, output free.
_INPUT_USD_PER_TOKEN = Decimal("0.042") / 1_000_000
_TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}


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
        response, hit = await self._cache.get_or_call(
            {"url": DECISIONS_URL, **payload}, lambda: self._post(payload)
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

    async def _post(self, payload: dict[str, Any]) -> CachedResponse:
        """One paid call: reserve a worst-case estimate, retry blips, charge the real cost."""
        ## A token is at least one byte, so the byte count bounds the input tokens.
        estimate = len(json.dumps(payload).encode()) * _INPUT_USD_PER_TOKEN
        with self._ledger.reserve(estimate) as charge:
            started = time.perf_counter()
            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(4),
                    wait=wait_exponential(multiplier=1, max=20),
                    retry=retry_if_exception(_is_transient),
                    reraise=True,
                ):
                    with attempt:
                        response = await self._http.post(DECISIONS_URL, json=payload)
                        response.raise_for_status()
            except httpx.HTTPStatusError as error:
                raise ProviderError(
                    f"Decisions API {error.response.status_code}: {error.response.text[:500]}"
                ) from error
            except httpx.TransportError as error:
                raise ProviderError(f"Decisions API unreachable: {error!r}") from error
            latency = time.perf_counter() - started
            body = response.json()
            charge(Decimal(str(_parse(body).usage.cost)))
        return CachedResponse(body=body, latency_s=latency)


def _is_transient(error: BaseException) -> bool:
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in _TRANSIENT_STATUS
    return isinstance(error, httpx.TransportError)


def _parse(body: dict[str, Any]) -> _Body:
    """Validate a response body; anything unexpected is the provider's error, not ours."""
    try:
        return _Body.model_validate(body)
    except ValidationError as error:
        raise ProviderError(f"unexpected Decisions API answer: {error}") from error
