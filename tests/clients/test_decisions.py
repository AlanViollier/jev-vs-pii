"""Decisions client against a fake transport: parses answers, charges once, caches, retries blips."""

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
from jev_vs_pii.clients.decisions import Choice, ChoiceAnswer, DecisionsClient, Noul, NoulAnswer
from jev_vs_pii.exceptions import BudgetExceeded, ProviderError

## Hand-written in the shape the live API returned on Sep 24.
_BODY = {
    "model": "typesafe/jev-1.13-20260917",
    "answers": {
        "w0": {"type": "noul", "noul": 0.95},
        "t0": {
            "type": "choice",
            "choice": "LOCATION",
            "probabilities": {"PERSON": 0, "LOCATION": 1},
            "confidence": 1,
        },
    },
    "usage": {"input_tokens": 438, "output_tokens": 102, "cost": 1.8396e-05},
    "id": "gen-dec-test",
}
_QUESTIONS: dict[str, Noul | Choice] = {
    "w0": Noul(instructions="Is 'Marie' personal information?"),
    "t0": Choice(
        instructions="What kind is 'Lyon'?", criteria={"PERSON": "a name", "LOCATION": "a place"}
    ),
}


class _Server:
    def __init__(self, *statuses: int) -> None:
        self.statuses = list(statuses)
        self.requests: list[dict[str, Any]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(json.loads(request.content))
        status = self.statuses.pop(0) if self.statuses else 200
        return httpx.Response(status, json=_BODY if status == 200 else {"error": {"code": status}})


def _client(tmp_path: Path, server: _Server, cap: str = "1") -> tuple[DecisionsClient, Ledger]:
    ledger = Ledger(tmp_path / "ledger.json", cap_usd=Decimal(cap))
    client = DecisionsClient(
        "test-key",
        "typesafe/jev-1.13",
        ledger,
        ResponseCache(tmp_path / "cache"),
        transport=httpx.MockTransport(server),
    )
    return client, ledger


def test_answers_parse_and_cost_is_charged(tmp_path: Path) -> None:
    server = _Server()
    client, ledger = _client(tmp_path, server)
    result = asyncio.run(client.ask("Send it to Marie in Lyon.", _QUESTIONS))
    assert result.answers["w0"] == NoulAnswer(type="noul", noul=0.95)
    assert isinstance(result.answers["t0"], ChoiceAnswer)
    assert result.answers["t0"].choice == "LOCATION"
    assert result.usage.cost_usd == Decimal("0.000018396")
    assert ledger.spent_usd == Decimal("0.000018396")
    assert server.requests[0]["questions"]["t0"]["criteria"] == {
        "PERSON": "a name",
        "LOCATION": "a place",
    }


def test_repeat_is_cached_uncharged_but_still_reports_the_real_cost(tmp_path: Path) -> None:
    server = _Server()
    client, ledger = _client(tmp_path, server)
    asyncio.run(client.ask("Send it to Marie in Lyon.", _QUESTIONS))
    again = asyncio.run(client.ask("Send it to Marie in Lyon.", _QUESTIONS))
    assert len(server.requests) == 1
    assert ledger.spent_usd == Decimal("0.000018396")
    assert (again.usage.calls, again.usage.cache_hits) == (1, 1)
    assert again.usage.cost_usd == Decimal("0.000018396")


def test_transient_error_is_retried(tmp_path: Path) -> None:
    server = _Server(503)
    client, _ = _client(tmp_path, server)
    result = asyncio.run(client.ask("Marie", _QUESTIONS))
    assert len(server.requests) == 2
    assert result.usage.calls == 1


def test_auth_error_is_a_provider_error_without_retry(tmp_path: Path) -> None:
    server = _Server(401)
    client, ledger = _client(tmp_path, server)
    with pytest.raises(ProviderError, match="401"):
        asyncio.run(client.ask("Marie", _QUESTIONS))
    assert len(server.requests) == 1
    assert ledger.spent_usd == 0


def test_call_that_could_pass_the_cap_is_never_sent(tmp_path: Path) -> None:
    server = _Server()
    client, _ = _client(tmp_path, server, cap="0.000001")
    with pytest.raises(BudgetExceeded):
        asyncio.run(client.ask("Marie " * 100, _QUESTIONS))
    assert server.requests == []


def test_client_builds_its_own_transport_when_none_is_given(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.json", cap_usd=Decimal("1"))
    DecisionsClient("k", "m", ledger, ResponseCache(tmp_path))
