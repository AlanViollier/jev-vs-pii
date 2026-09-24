"""Generative models through OpenRouter's chat endpoint (Haiku only, as the ceiling)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from pii_bench.clients.budget import Ledger
from pii_bench.clients.cache import ResponseCache
from pii_bench.schema import Usage


class Message(BaseModel):
    """One chat turn."""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatResult(BaseModel):
    """Generated text plus what the call cost."""

    text: str
    usage: Usage


class ChatClient:
    """Async chat client; every call is budget-checked and cached."""

    def __init__(self, api_key: str, ledger: Ledger, cache: ResponseCache) -> None:
        raise NotImplementedError

    async def complete(
        self,
        model: str,
        messages: list[Message],
        json_schema: dict[str, Any] | None = None,
    ) -> ChatResult:
        """Run one completion at temperature 0.

        Parameters
        ----------
        model:
            OpenRouter model id.
        messages:
            The conversation.
        json_schema:
            When set, the model must answer with JSON matching it.

        Returns
        -------
        ChatResult
            Raises `BudgetExceeded` or `ProviderError` like `DecisionsClient.ask`.
        """
        raise NotImplementedError
