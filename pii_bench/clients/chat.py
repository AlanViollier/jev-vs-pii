"""Generative models through OpenRouter's chat endpoint, at temperature 0, optionally held to a JSON schema."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ValidationError

from pii_bench.clients.budget import Ledger
from pii_bench.clients.cache import ResponseCache
from pii_bench.clients.http import paid_post
from pii_bench.config import ModelSpec
from pii_bench.exceptions import ProviderError
from pii_bench.schema import Usage

CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
## Room for a tagged rewrite of the longest TAB judgment; also caps the budget hold.
MAX_OUTPUT_TOKENS = 8192
## Thinking gets its own budget on top, or it can use up the answer's.
MAX_REASONING_TOKENS = 8192


class Message(BaseModel):
    """One chat turn."""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatResult(BaseModel):
    """Generated text, whether it hit the output cap, what it cost, and who served it."""

    text: str
    truncated: bool
    provider: str
    usage: Usage


class _Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    cost: float


class _ChoiceMessage(BaseModel):
    content: str | None


class _Choice(BaseModel):
    message: _ChoiceMessage
    finish_reason: str | None


class _Body(BaseModel):
    provider: str
    choices: list[_Choice]
    usage: _Usage


class ChatClient:
    """Async chat client; every call is budget-checked and cached."""

    def __init__(
        self,
        api_key: str,
        ledger: Ledger,
        cache: ResponseCache,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._ledger = ledger
        self._cache = cache
        self._http = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"}, timeout=300, transport=transport
        )

    async def complete(
        self,
        model: ModelSpec,
        messages: list[Message],
        json_schema: dict[str, Any] | None = None,
    ) -> ChatResult:
        """Run one completion at temperature 0.

        Parameters
        ----------
        model:
            Which model, with the prices that bound its budget hold.
        messages:
            The conversation.
        json_schema:
            When set, the answer must be JSON matching it, and only providers that
            enforce schemas may serve the call.

        Returns
        -------
        ChatResult
            Raises `BudgetExceeded` or `ProviderError` like `DecisionsClient.ask`.
        """
        max_tokens = MAX_OUTPUT_TOKENS + (MAX_REASONING_TOKENS if model.reasoning else 0)
        payload: dict[str, Any] = {
            "model": model.id,
            "messages": [message.model_dump() for message in messages],
            ## No seed: Anthropic's endpoints reject it, and with `require_parameters` that
            ## would rule them out entirely.
            "temperature": 0,
            "max_tokens": max_tokens,
        }
        if model.reasoning is not None:
            payload["reasoning"] = (
                {"enabled": True, "max_tokens": MAX_REASONING_TOKENS}
                if model.reasoning
                else {"enabled": False}
            )
        if json_schema is not None:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "answer", "strict": True, "schema": json_schema},
            }
            payload["provider"] = {"require_parameters": True}
        if model.provider is not None:
            payload["provider"] = {
                "order": [model.provider],
                "allow_fallbacks": False,
                **payload.get("provider", {}),
            }
        ## A token is at least one byte, so bytes bound the input; the output cap bounds the rest.
        estimate = (
            len(json.dumps(payload).encode()) * model.input_usd_per_m
            + max_tokens * model.output_usd_per_m
        ) / 1_000_000
        response, hit = await self._cache.get_or_call(
            {"url": CHAT_URL, **payload},
            lambda: paid_post(self._http, CHAT_URL, payload, self._ledger, estimate, _cost),
        )
        body = _parse(response.body)
        choice = body.choices[0]
        return ChatResult(
            text=choice.message.content or "",
            truncated=choice.finish_reason == "length",
            provider=body.provider,
            usage=Usage(
                calls=1,
                cache_hits=int(hit),
                input_tokens=body.usage.prompt_tokens,
                output_tokens=body.usage.completion_tokens,
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
        raise ProviderError(f"unexpected chat answer: {error}") from error
