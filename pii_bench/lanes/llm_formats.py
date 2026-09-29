"""The three ways an LLM can answer "where is the PII": say it back, give offsets, or tag a rewrite.

Each format is what it asks the model, the schema its answer must follow, and how that
answer becomes spans. Parsers raise `ValidationError` or `AlignmentError` on an unusable answer.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from pii_bench.align import Mention, find_mentions, parse_tagged
from pii_bench.schema import Span
from pii_bench.taxonomy import DEFINITIONS, Coarse

Parser = Callable[[str, str], tuple[list[Span], int]]


@dataclass(frozen=True)
class AnswerFormat:
    """One output format: instructions, optional JSON schema, parser (source, answer) -> (spans, dropped)."""

    name: str
    instructions: str
    json_schema: dict[str, Any] | None
    parse: Parser


class _SaidItem(BaseModel):
    text: str
    type: Coarse


class _Said(BaseModel):
    items: list[_SaidItem]


class _Offset(BaseModel):
    start: int
    end: int
    type: Coarse


class _Offsets(BaseModel):
    items: list[_Offset]


def _items_schema(properties: dict[str, Any]) -> dict[str, Any]:
    """Strict JSON schema for `{"items": [{...properties, "type": <coarse label>}]}`."""
    item = {
        "type": "object",
        "properties": {**properties, "type": {"type": "string", "enum": list(DEFINITIONS)}},
        "required": [*properties, "type"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {"items": {"type": "array", "items": item}},
        "required": ["items"],
        "additionalProperties": False,
    }


def _parse_sayback(source: str, answer: str) -> tuple[list[Span], int]:
    items = _Said.model_validate_json(answer).items
    return find_mentions(source, [Mention(text=item.text, label=item.type) for item in items])


def _parse_offsets(source: str, answer: str) -> tuple[list[Span], int]:
    items = _Offsets.model_validate_json(answer).items
    spans = [
        Span(start=item.start, end=item.end, label=item.type)
        for item in items
        if 0 <= item.start < item.end <= len(source)
    ]
    return spans, len(items) - len(spans)


SAYBACK = AnswerFormat(
    name="sayback",
    instructions=(
        "List every piece of personal information in the text. Copy each one exactly as it "
        "is written, list each distinct string once, and give its type."
    ),
    json_schema=_items_schema({"text": {"type": "string"}}),
    parse=_parse_sayback,
)

OFFSETS = AnswerFormat(
    name="offsets",
    instructions=(
        "List every piece of personal information in the text as character offsets: `start` "
        "is the 0-based index of its first character, `end` the index just after its last. "
        "Give each one's type."
    ),
    json_schema=_items_schema({"start": {"type": "integer"}, "end": {"type": "integer"}}),
    parse=_parse_offsets,
)

TAGGED = AnswerFormat(
    name="tagged",
    instructions=(
        "Rewrite the text exactly as given, changing nothing, but wrap every piece of personal "
        "information in a tag naming its type, like <PERSON>Jane Roe</PERSON>. "
        "Answer with the rewritten text only."
    ),
    json_schema=None,
    parse=parse_tagged,
)

FORMATS: dict[str, AnswerFormat] = {f.name: f for f in (SAYBACK, OFFSETS, TAGGED)}
