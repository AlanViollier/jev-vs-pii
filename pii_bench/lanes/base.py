"""What every lane looks like from the outside, and what the LLM lanes need from a client."""

from __future__ import annotations

from typing import Any, Protocol

from pii_bench.clients.chat import ChatResult, Message
from pii_bench.schema import Doc, LaneInfo, Prediction


class Lane(Protocol):
    """One standalone PII method: a doc in, spans (and word scores if it has them) out."""

    info: LaneInfo

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        ...


class Completer(Protocol):
    """Anything that completes a chat: `ChatClient` (API) or `LocalClient` (ollama)."""

    async def complete(
        self,
        model: str,
        messages: list[Message],
        json_schema: dict[str, Any] | None = None,
    ) -> ChatResult:
        """Run one completion."""
        ...
