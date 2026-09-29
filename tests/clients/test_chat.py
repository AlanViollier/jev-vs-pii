"""Chat client against a fake transport: schema request shape, cost charged once, truncation seen."""

from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from jev_vs_pii.clients.budget import Ledger
from jev_vs_pii.clients.cache import ResponseCache
from jev_vs_pii.clients.chat import ChatClient, Message
from jev_vs_pii.config import ModelSpec
from jev_vs_pii.exceptions import BudgetExceeded, ProviderError

_MODEL = ModelSpec(
    id="vendor/small-model", input_usd_per_m=Decimal("0.05"), output_usd_per_m=Decimal("0.2")
)
_MESSAGES = [Message(role="user", content="Find the PII in: Call Marie.")]


def _body(finish_reason: str = "stop") -> dict[str, Any]:
    """Hand-written in the shape the live endpoint returned on Sep 29."""
    return {
        "provider": "SomeHost",
        "model": _MODEL.id,
        "choices": [
            {"message": {"content": '{"items": []}'}, "finish_reason": finish_reason},
        ],
        "usage": {"prompt_tokens": 32, "completion_tokens": 41, "cost": 9.45585e-06},
    }


class _Server:
    def __init__(self, body: dict[str, Any]) -> None:
        self.body = body
        self.requests: list[dict[str, Any]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(json.loads(request.content))
        return httpx.Response(200, json=self.body)


def _client(tmp_path: Path, server: _Server, cap: str = "1") -> tuple[ChatClient, Ledger]:
    ledger = Ledger(tmp_path / "ledger.json", cap_usd=Decimal(cap))
    client = ChatClient(
        "test-key", ledger, ResponseCache(tmp_path / "cache"), transport=httpx.MockTransport(server)
    )
    return client, ledger


def test_schema_call_is_strict_and_routed_to_providers_that_enforce_it(tmp_path: Path) -> None:
    server = _Server(_body())
    client, ledger = _client(tmp_path, server)
    schema = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}
    result = asyncio.run(client.complete(_MODEL, _MESSAGES, json_schema=schema))
    sent = server.requests[0]
    assert sent["temperature"] == 0
    assert sent["response_format"]["json_schema"]["strict"] is True
    assert sent["provider"] == {"require_parameters": True}
    assert (result.text, result.truncated, result.provider) == ('{"items": []}', False, "SomeHost")
    assert ledger.spent_usd == Decimal("0.00000945585")


def test_plain_call_sends_no_schema_and_repeat_is_free(tmp_path: Path) -> None:
    server = _Server(_body())
    client, ledger = _client(tmp_path, server)
    asyncio.run(client.complete(_MODEL, _MESSAGES))
    again = asyncio.run(client.complete(_MODEL, _MESSAGES))
    assert "response_format" not in server.requests[0]
    assert len(server.requests) == 1
    assert again.usage.cache_hits == 1
    assert ledger.spent_usd == Decimal("0.00000945585")


def test_hitting_the_output_cap_is_reported(tmp_path: Path) -> None:
    client, _ = _client(tmp_path, _Server(_body(finish_reason="length")))
    assert asyncio.run(client.complete(_MODEL, _MESSAGES)).truncated


def test_hold_covers_the_whole_output_cap(tmp_path: Path) -> None:
    ## 8,192 output tokens at $0.2/M is ~$0.0016, so a $0.001 cap refuses before sending.
    server = _Server(_body())
    client, _ = _client(tmp_path, server, cap="0.001")
    with pytest.raises(BudgetExceeded):
        asyncio.run(client.complete(_MODEL, _MESSAGES))
    assert server.requests == []


def test_error_body_is_a_provider_error_and_not_charged(tmp_path: Path) -> None:
    client, ledger = _client(tmp_path, _Server({"error": {"message": "upstream"}}))
    with pytest.raises(ProviderError):
        asyncio.run(client.complete(_MODEL, _MESSAGES))
    assert ledger.spent_usd == 0


@pytest.mark.parametrize("reasoning", [True, False])
def test_reasoning_switch_is_sent_only_when_set(tmp_path: Path, reasoning: bool) -> None:
    server = _Server(_body())
    client, _ = _client(tmp_path, server)
    asyncio.run(client.complete(_MODEL.model_copy(update={"reasoning": reasoning}), _MESSAGES))
    asyncio.run(client.complete(_MODEL, [Message(role="user", content="other")]))
    assert server.requests[0]["reasoning"]["enabled"] is reasoning
    assert server.requests[0]["max_tokens"] == (16384 if reasoning else 8192)
    assert "reasoning" not in server.requests[1]


def test_restricted_providers_are_the_only_ones_allowed(tmp_path: Path) -> None:
    server = _Server(_body())
    client, _ = _client(tmp_path, server)
    restricted = _MODEL.model_copy(update={"providers": ["DeepInfra", "Parasail"]})
    asyncio.run(client.complete(restricted, _MESSAGES, json_schema={"type": "object"}))
    assert server.requests[0]["provider"] == {
        "only": ["DeepInfra", "Parasail"],
        "require_parameters": True,
    }
