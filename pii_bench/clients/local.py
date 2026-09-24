"""Local generative models through ollama. Free, so no ledger; cached for replay and reruns."""

from __future__ import annotations

from typing import Any

from pii_bench.clients.cache import ResponseCache
from pii_bench.clients.chat import ChatResult, Message


class LocalClient:
    """Async ollama client with the same `complete` shape as `ChatClient`."""

    def __init__(self, host: str, cache: ResponseCache) -> None:
        raise NotImplementedError

    async def complete(
        self,
        model: str,
        messages: list[Message],
        json_schema: dict[str, Any] | None = None,
    ) -> ChatResult:
        """Run one completion at temperature 0 on the local machine.

        Parameters
        ----------
        model:
            ollama model tag, e.g. `qwen3:8b`.
        messages:
            The conversation.
        json_schema:
            When set, the model must answer with JSON matching it.

        Returns
        -------
        ChatResult
            `usage.cost_usd` is always 0; latency is wall-clock on this machine.
        """
        raise NotImplementedError
