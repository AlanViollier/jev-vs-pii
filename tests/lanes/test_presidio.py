"""Presidio lane, when the optional NER extra is installed: coarse types and in-range spans."""

from __future__ import annotations

import asyncio

import pytest

from pii_bench.schema import Doc

pytest.importorskip("presidio_analyzer")
pytest.importorskip("en_core_web_lg")

from pii_bench.lanes.presidio import PresidioLane  # noqa: E402  # after the skips on purpose


def test_presidio_finds_a_name_and_an_email_with_coarse_types() -> None:
    text = "Please forward the file to John Smith at john.smith@example.com tomorrow."
    doc = Doc(id="d", dataset="ai4privacy", split="test", text=text, gold=())
    prediction = asyncio.run(PresidioLane().predict(doc))
    found = {(text[span.start : span.end], span.label) for span in prediction.spans}
    assert ("John Smith", "PERSON") in found
    assert ("john.smith@example.com", "CONTACT") in found
    assert all(0 <= span.start < span.end <= len(text) for span in prediction.spans)
