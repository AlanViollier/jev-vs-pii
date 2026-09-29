"""Regex lane: each format is found with its type, prose and bare numbers are left alone."""

from __future__ import annotations

import asyncio

import pytest

from pii_bench.lanes.mask_all import MaskAllLane
from pii_bench.lanes.regex import RegexLane, find_patterns
from pii_bench.schema import Doc


def _found(text: str) -> list[tuple[str, str | None]]:
    return [(text[span.start : span.end], span.label) for span in find_patterns(text)]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Write to jo.ann+bills@mail.example.org today",
            ("jo.ann+bills@mail.example.org", "CONTACT"),
        ),
        ("Login from 192.168.10.254 failed", ("192.168.10.254", "CONTACT")),
        ("Host fe80:0:0:0:200:f8ff:fe21:67cf is up", ("fe80:0:0:0:200:f8ff:fe21:67cf", "CONTACT")),
        ("Call +44 20 7946 0958 now", ("+44 20 7946 0958", "CONTACT")),
        ("Card 4111 1111 1111 1111 expired", ("4111 1111 1111 1111", "ID")),
        ("Born 1987-03-14 in town", ("1987-03-14", "DATETIME")),
        ("Signed 14/03/1987 by both", ("14/03/1987", "DATETIME")),
        ("Hearing on 3rd of March, 2004 at noon", ("3rd of March, 2004", "DATETIME")),
        ("Filed Sept. 9, 2011 late", ("Sept. 9, 2011", "DATETIME")),
        ("Meet at 7:45 pm sharp", ("7:45 pm", "DATETIME")),
        ("Application no. 28341/95 was lodged", ("28341/95", "ID")),
        ("Ticket AB12345C reopened", ("AB12345C", "ID")),
    ],
)
def test_each_format_is_found_with_its_type(text: str, expected: tuple[str, str]) -> None:
    assert _found(text) == [expected]


@pytest.mark.parametrize(
    "text",
    [
        "The court held that there had been no violation.",
        "In 2004 the applicant was 35 years old and paid 1200 euros.",
        "Clock read 12:30:45 on the wall",
    ],
)
def test_prose_years_and_small_numbers_are_left_alone(text: str) -> None:
    assert all(label == "DATETIME" for _, label in _found(text))
    assert "2004" not in [found for found, _ in _found(text)]


def test_overlapping_matches_keep_the_leftmost_longest() -> None:
    text = "Card 4111-1111-1111-1111"
    assert _found(text) == [("4111-1111-1111-1111", "ID")]
    spans = find_patterns("a 1987-03-14 b 1987-03-15")
    assert all(left.end <= right.start for left, right in zip(spans, spans[1:], strict=False))


def test_lanes_return_a_prediction_for_the_doc() -> None:
    doc = Doc(id="d1", dataset="ai4privacy", split="test", text="Mail a@b.co", gold=())
    regex = asyncio.run(RegexLane().predict(doc))
    floor = asyncio.run(MaskAllLane().predict(doc))
    assert (regex.doc_id, regex.lane_id, len(regex.spans)) == ("d1", "regex", 1)
    assert [(span.start, span.end) for span in floor.spans] == [(0, len(doc.text))]
