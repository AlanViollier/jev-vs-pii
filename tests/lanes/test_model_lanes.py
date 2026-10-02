"""Decision and LLM lanes against fake servers: questions per word, batching, parsing, failure policy."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest

from jev_vs_pii.clients import ChatClient, DecisionsClient, Ledger, ResponseCache
from jev_vs_pii.config import AppSettings, ModelSpec
from jev_vs_pii.exceptions import ConfigError
from jev_vs_pii.lanes import designs, jev
from jev_vs_pii.lanes.designs import BIO, TYPED, TYPED_SKIP, WORDS, in_context
from jev_vs_pii.lanes.registry import LaneDeps, build_lane
from jev_vs_pii.schema import Doc
from jev_vs_pii.taxonomy import DEFINITIONS, definition
from jev_vs_pii.words import split_words

_DOC = Doc(
    id="d1", dataset="ai4privacy", split="test", text="Please call Marie Dupont today.", gold=()
)
_NAMES = {"Marie", "Dupont"}
_MODEL = ModelSpec(id="vendor/m", input_usd_per_m=Decimal("0.1"), output_usd_per_m=Decimal("0.1"))
_USAGE = {"input_tokens": 100, "output_tokens": 10, "cost": 0.00001}

Handler = Callable[[dict[str, Any]], dict[str, Any]]


class _Server:
    def __init__(self, handler: Handler) -> None:
        self.handler = handler
        self.requests: list[dict[str, Any]] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        self.requests.append(body)
        return httpx.Response(200, json=self.handler(body))


def _jev_answers(body: dict[str, Any]) -> dict[str, Any]:
    """Yes for the two names, and a word continues the one before it only inside the name."""
    answers: dict[str, Any] = {}
    for key, question in body["questions"].items():
        word = re.search(r"\[(.+?)\]", question["instructions"]).group(1)  # type: ignore[union-attr]  # every question brackets its word
        if question["type"] == "choice":
            person = 0.9 if word in _NAMES else 0.05
            probs = {label: 0.0 for label in question["criteria"]}
            probs.update({"PERSON": person, "NONE": 1 - person})
            answers[key] = {
                "type": "choice",
                "choice": "PERSON",
                "probabilities": probs,
                "confidence": 0.9,
            }
        elif key.startswith("c"):
            answers[key] = {"type": "noul", "noul": 0.9 if word == "Dupont" else 0.1}
        else:
            answers[key] = {"type": "noul", "noul": 0.95 if word in _NAMES else 0.02}
    return {"answers": answers, "usage": _USAGE}


def _chat_answer(content: str, finish_reason: str = "stop") -> Handler:
    return lambda _: {
        "provider": "SomeHost",
        "choices": [{"message": {"content": content}, "finish_reason": finish_reason}],
        "usage": {"prompt_tokens": 50, "completion_tokens": 20, "cost": 0.00002},
    }


def _deps(tmp_path: Path, jev_server: _Server, chat_server: _Server) -> LaneDeps:
    ledger = Ledger(tmp_path / "ledger.json", Decimal("1"))
    cache = ResponseCache(tmp_path / "cache")
    return LaneDeps(
        settings=AppSettings(models={"small": _MODEL}),
        decisions=DecisionsClient(
            "k", "typesafe/jev", ledger, cache, transport=httpx.MockTransport(jev_server)
        ),
        chat=ChatClient("k", ledger, cache, transport=httpx.MockTransport(chat_server)),
    )


def _predict(tmp_path: Path, lane_id: str, chat: Handler = _chat_answer("{}")) -> Any:
    jev_server, chat_server = _Server(_jev_answers), _Server(chat)
    lane = build_lane(lane_id, _deps(tmp_path, jev_server, chat_server))
    prediction = asyncio.run(lane.predict(_DOC))
    return prediction, jev_server, chat_server


def _found(prediction: Any) -> list[str]:
    return [_DOC.text[span.start : span.end] for span in prediction.spans]


def test_context_brackets_the_word_among_its_neighbours() -> None:
    words = split_words("Please call Marie Dupont today, thanks.")
    assert in_context("Please call Marie Dupont today, thanks.", words, 3) == (
        "Please call Marie [Dupont] today, thanks"
    )


@pytest.mark.parametrize(
    "lane_id", ["decision_words:jev", "decision_bio:jev", "decision_typed:jev"]
)
def test_jev_lanes_score_every_word_and_decode_the_name(tmp_path: Path, lane_id: str) -> None:
    prediction, jev_server, _ = _predict(tmp_path, lane_id)
    assert prediction.word_scores is not None
    assert len(prediction.word_scores) == len(split_words(_DOC.text))
    assert _found(prediction) == ["Marie Dupont"]
    assert prediction.usage.calls == len(jev_server.requests) == 1
    assert "PERSON:" in jev_server.requests[0]["state"]


def test_jev_questions_per_word_by_design(tmp_path: Path) -> None:
    words = split_words(_DOC.text)
    assert set(WORDS.ask(_DOC, words, 2)) == {"p2"}
    assert set(BIO.ask(_DOC, words, 0)) == {"p0"}
    assert set(BIO.ask(_DOC, words, 2)) == {"p2", "c2"}
    typed = TYPED.ask(_DOC, words, 2)["t2"]
    assert set(typed.criteria) - {"NONE"} == set(DEFINITIONS)  # type: ignore[union-attr]  # TYPED asks a choice
    assert typed.criteria["NONE"] == "not personal information"  # type: ignore[union-attr]


def test_typed_scores_carry_the_type(tmp_path: Path) -> None:
    prediction, _, _ = _predict(tmp_path, "decision_typed:jev")
    assert [span.label for span in prediction.spans] == ["PERSON"]


@pytest.fixture
def _few_stop_words(monkeypatch: pytest.MonkeyPatch) -> None:
    ## spaCy's list comes with the ner extra, absent in CI.
    monkeypatch.setattr(designs, "_stop_words", lambda: frozenset({"please", "today"}))


@pytest.mark.usefixtures("_few_stop_words")
def test_skip_never_asks_about_a_stop_word_and_scores_it_zero() -> None:
    words = split_words(_DOC.text)
    assert TYPED_SKIP.ask(_DOC, words, 0) == {}
    assert TYPED_SKIP.score({}, words, 0).p_pii == 0.0
    assert TYPED_SKIP.ask(_DOC, words, 2) == TYPED.ask(_DOC, words, 2)


@pytest.mark.usefixtures("_few_stop_words")
def test_skip_lane_sends_the_typed_questions_minus_stop_words(tmp_path: Path) -> None:
    typed, typed_server, _ = _predict(tmp_path / "typed", "decision_typed:jev")
    skip, skip_server, _ = _predict(tmp_path / "skip", "decision_typed_skip:jev")
    asked, kept = typed_server.requests[0]["questions"], skip_server.requests[0]["questions"]
    assert set(asked) - set(kept) == {"t0", "t4"}
    assert all(kept[key] == asked[key] for key in kept)
    assert skip_server.requests[0]["state"] == typed_server.requests[0]["state"]
    assert _found(skip) == _found(typed) == ["Marie Dupont"]
    assert skip.lane_id == "decision_typed_skip:jev"


def test_long_docs_are_split_into_concurrent_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ## Room for the state plus about two questions per call: 5 words -> 3 calls.
    state_chars = len(json.dumps(f"{definition(_DOC)}\n\nText:\n{_DOC.text}"))
    monkeypatch.setattr(jev, "MAX_INPUT_TOKENS", (state_chars + 260) / 2.4)
    prediction, jev_server, _ = _predict(tmp_path, "decision_words:jev")
    assert len(jev_server.requests) == 3
    assert sorted(len(r["questions"]) for r in jev_server.requests) == [1, 2, 2]
    assert prediction.usage.calls == 3
    assert prediction.usage.cost_usd == Decimal("0.00003")
    assert _found(prediction) == ["Marie Dupont"]


def test_sayback_lane_places_what_the_model_said(tmp_path: Path) -> None:
    answer = json.dumps(
        {
            "items": [
                {"text": "Marie Dupont", "type": "PERSON"},
                {"text": "Paris", "type": "LOCATION"},
            ]
        }
    )
    prediction, _, chat_server = _predict(tmp_path, "llm_sayback:small", _chat_answer(answer))
    assert _found(prediction) == ["Marie Dupont"]
    assert (prediction.dropped, prediction.failed) == (1, False)
    sent = chat_server.requests[0]
    assert sent["model"] == "vendor/m"
    assert sent["messages"][1]["content"] == _DOC.text
    assert prediction.lane_id == "llm_sayback:small"


def test_offsets_lane_drops_offsets_outside_the_text(tmp_path: Path) -> None:
    answer = json.dumps(
        {
            "items": [
                {"start": 12, "end": 24, "type": "PERSON"},
                {"start": 30, "end": 99, "type": "ID"},
            ]
        }
    )
    prediction, _, _ = _predict(tmp_path, "llm_offsets:small", _chat_answer(answer))
    assert _found(prediction) == ["Marie Dupont"]
    assert prediction.dropped == 1


def test_tagged_lane_sends_no_schema(tmp_path: Path) -> None:
    answer = "Please call <PERSON>Marie Dupont</PERSON> today."
    prediction, _, chat_server = _predict(tmp_path, "llm_tagged:small", _chat_answer(answer))
    assert _found(prediction) == ["Marie Dupont"]
    assert "response_format" not in chat_server.requests[0]


@pytest.mark.parametrize(
    ("lane_id", "handler", "failure"),
    [
        ("llm_sayback:small", _chat_answer("not json"), "unparseable"),
        ("llm_sayback:small", _chat_answer('{"items": [', finish_reason="length"), "truncated"),
        ("llm_tagged:small", _chat_answer("Here is a list: <PERSON>Marie</PERSON>"), "misaligned"),
    ],
)
def test_unusable_answer_counts_as_finding_nothing_and_says_why(
    tmp_path: Path, lane_id: str, handler: Handler, failure: str
) -> None:
    prediction, _, _ = _predict(tmp_path, lane_id, handler)
    assert (prediction.failed, prediction.failure) == (True, failure)
    assert prediction.spans == ()
    assert prediction.usage.calls == 1
    assert prediction.answer and prediction.provider == "SomeHost"


@pytest.mark.parametrize(
    "lane_id",
    [
        "llm_sayback:nope",
        "regex:small",
        "nope",
        "llm_sayback",
        "decision_words",
        "decision_words:nope",
    ],
)
def test_bad_lane_ids_are_config_errors(tmp_path: Path, lane_id: str) -> None:
    with pytest.raises(ConfigError):
        build_lane(lane_id, _deps(tmp_path, _Server(_jev_answers), _Server(_chat_answer("{}"))))
