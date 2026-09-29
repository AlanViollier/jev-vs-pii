"""Alignment: said-back strings and tagged rewrites land on the right source offsets."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pii_bench.align import Mention, find_mentions, parse_tagged
from pii_bench.exceptions import AlignmentError


def _texts(source: str, spans: list[tuple[int, int]]) -> list[str]:
    return [source[start:end] for start, end in spans]


def test_mentions_match_every_occurrence_ignoring_case_and_spacing() -> None:
    source = "Marie Dupont called. Later MARIE  DUPONT wrote to Marie."
    spans, missing = find_mentions(source, [Mention(text="marie dupont", label="PERSON")])
    assert _texts(source, [(s.start, s.end) for s in spans]) == ["Marie Dupont", "MARIE  DUPONT"]
    assert {s.label for s in spans} == {"PERSON"}
    assert missing == 0


def test_mention_tolerates_punctuation_between_its_words() -> None:
    source = "As Mr. Daniel said, the house in Lyon, France was sold."
    spans, missing = find_mentions(
        source,
        [Mention(text="Mr Daniel", label="PERSON"), Mention(text="Lyon France", label="LOCATION")],
    )
    assert _texts(source, [(s.start, s.end) for s in spans]) == ["Mr. Daniel", "Lyon, France"]
    assert missing == 0


def test_mention_never_matches_inside_a_longer_word() -> None:
    spans, _ = find_mentions("Also Al said", [Mention(text="Al", label="PERSON")])
    assert [(s.start, s.end) for s in spans] == [(5, 7)]


def test_mentions_found_nowhere_are_counted_and_duplicates_collapse() -> None:
    spans, missing = find_mentions(
        "Call 555-0100",
        [
            Mention(text="555-0100", label="CONTACT"),
            Mention(text="555-0100", label="CONTACT"),
            Mention(text="Bob", label="PERSON"),
        ],
    )
    assert len(spans) == 1
    assert missing == 1


def test_tagged_rewrite_identical_to_source() -> None:
    source = "Call Marie at 555-0100."
    tagged = "Call <PERSON>Marie</PERSON> at <CONTACT>555-0100</CONTACT>."
    spans, dropped = parse_tagged(source, tagged)
    assert _texts(source, [(s.start, s.end) for s in spans]) == ["Marie", "555-0100"]
    assert [s.label for s in spans] == ["PERSON", "CONTACT"]
    assert dropped == 0


def test_tagged_rewrite_with_small_drift_still_aligns() -> None:
    source = "Please call Marie Dupont at 555-0100 before Friday, thank you."
    tagged = "Please call <PERSON>Marie Dupont</PERSON> at <CONTACT>555-0100</CONTACT> before friday, thanks you."
    spans, _ = parse_tagged(source, tagged)
    assert _texts(source, [(s.start, s.end) for s in spans]) == ["Marie Dupont", "555-0100"]


def test_unmatched_tags_are_ignored() -> None:
    source = "Call Marie now."
    spans, _ = parse_tagged(source, "Call <PERSON>Marie</LOCATION> now.")
    assert spans == []


def test_rewrite_that_drifted_too_far_raises() -> None:
    with pytest.raises(AlignmentError):
        parse_tagged("Call Marie at 555-0100 please.", "Here is the <PERSON>answer</PERSON>.")


@settings(max_examples=60)
@given(
    words=st.lists(st.text(alphabet="abcdefg", min_size=1, max_size=6), min_size=1, max_size=20),
    data=st.data(),
)
def test_tagging_any_words_round_trips(words: list[str], data: st.DataObject) -> None:
    source = " ".join(words)
    picked = sorted(set(data.draw(st.lists(st.integers(0, len(words) - 1), max_size=5))))
    tagged = " ".join(f"<ID>{word}</ID>" if i in picked else word for i, word in enumerate(words))
    spans, dropped = parse_tagged(source, tagged)
    assert [source[s.start : s.end] for s in spans] == [words[i] for i in picked]
    assert dropped == 0
