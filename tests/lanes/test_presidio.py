"""Presidio lane, when the optional NER extra is installed: coarse types and in-range spans."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast

import pytest

from jev_vs_pii.schema import Doc, LaneInfo

pytest.importorskip("presidio_analyzer")
pytest.importorskip("en_core_web_lg")

from jev_vs_pii.lanes.presidio import PresidioLane  # noqa: E402  # after the skips on purpose


def test_presidio_finds_a_name_and_an_email_with_coarse_types() -> None:
    text = "Please forward the file to John Smith at john.smith@example.com tomorrow."
    doc = Doc(id="d", dataset="ai4privacy", split="test", text=text, gold=())
    prediction = asyncio.run(PresidioLane().predict(doc))
    found = {(text[span.start : span.end], span.label) for span in prediction.spans}
    assert ("John Smith", "PERSON") in found
    assert ("john.smith@example.com", "CONTACT") in found
    assert all(0 <= span.start < span.end <= len(text) for span in prediction.spans)


def test_presidio_order_is_fixed_when_one_range_gets_two_types() -> None:
    text = "Account 123456789 on file."
    doc = Doc(id="d", dataset="ai4privacy", split="test", text=text, gold=())
    results = [
        SimpleNamespace(start=8, end=17, entity_type="PHONE_NUMBER", score=0.4),
        SimpleNamespace(start=8, end=17, entity_type="US_BANK_NUMBER", score=0.4),
    ]
    spans = []
    for order in (results, results[::-1]):
        lane = PresidioLane.__new__(PresidioLane)
        lane.info = LaneInfo(id="presidio", family="ner")
        lane._analyzer = cast(
            Any, SimpleNamespace(analyze=lambda text, language, order=order: order)
        )
        spans.append(asyncio.run(lane.predict(doc)).spans)
    assert spans[0] == spans[1]
    assert [span.label for span in spans[0]] == ["CONTACT", "ID"]
