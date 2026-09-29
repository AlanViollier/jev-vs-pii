"""Word splitting keeps exact offsets; a word is covered by any span sharing a character with it."""

from __future__ import annotations

import unicodedata

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from jev_vs_pii.schema import Span
from jev_vs_pii.words import covering_spans, split_words

_texts = st.text(
    alphabet=st.one_of(
        st.sampled_from(" \t\n.,;:!?()[]\"'—-@+$€#/"),
        st.characters(codec="utf-8"),
    ),
    max_size=200,
)


def _is_punct(char: str) -> bool:
    return unicodedata.category(char).startswith("P")


@settings(max_examples=100)
@given(_texts)
def test_words_point_back_into_text_in_order(text: str) -> None:
    words = split_words(text)
    for word in words:
        assert text[word.start : word.end] == word.text
        assert not any(char.isspace() for char in word.text)
        assert not _is_punct(word.text[0])
        assert not _is_punct(word.text[-1])
    for left, right in zip(words, words[1:], strict=False):
        assert left.end < right.start


@settings(max_examples=100)
@given(_texts)
def test_only_whitespace_and_punctuation_fall_between_words(text: str) -> None:
    covered = {i for word in split_words(text) for i in range(word.start, word.end)}
    for i, char in enumerate(text):
        if i not in covered:
            assert char.isspace() or _is_punct(char)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Dupont,", ["Dupont"]),
        ("(Lyon)", ["Lyon"]),
        ("rue 12.", ["rue", "12"]),
        ("nora@x.test.", ["nora@x.test"]),
        ("call +33 6 12", ["call", "+33", "6", "12"]),
        ("cost $40 or 12€", ["cost", "$40", "or", "12€"]),
        ("Dupont's file", ["Dupont's", "file"]),
        ("a — b", ["a", "b"]),
        ("-5 degrees", ["5", "degrees"]),
        ("the U.S.", ["the", "U.S"]),
        ("a + b", ["a", "+", "b"]),
        ("", []),
        ("  \n\t ", []),
    ],
)
def test_edge_punctuation_trimmed_symbols_kept(text: str, expected: list[str]) -> None:
    assert [word.text for word in split_words(text)] == expected


def test_offsets_skip_leading_punctuation() -> None:
    (word,) = split_words('  "Marie"')
    assert (word.start, word.end) == (3, 8)


def test_word_is_covered_when_it_overlaps_any_span() -> None:
    text = "Send it to Marie Dupont at Lyon today."
    words = split_words(text)
    marie = text.index("Marie")
    lyon = text.index("Lyon")
    # the Lyon span covers only "yo": a partial overlap still covers the word
    name = Span(start=marie, end=marie + len("Marie Dupont"), label="PERSON")
    city = Span(start=lyon + 1, end=lyon + 3, label="LOCATION")
    covering = covering_spans(words, [city, name])
    assert len(covering) == len(words)
    assert [(w.text, span.label) for w, span in zip(words, covering, strict=True) if span] == [
        ("Marie", "PERSON"),
        ("Dupont", "PERSON"),
        ("Lyon", "LOCATION"),
    ]


def test_span_touching_a_word_edge_does_not_cover_it() -> None:
    words = split_words("ab cd")
    assert covering_spans(words, [Span(start=2, end=3)]) == [None, None]


def test_earliest_starting_span_wins_a_shared_word() -> None:
    words = split_words("ab cd")
    early = Span(start=0, end=4, label="PERSON")
    late = Span(start=3, end=5, label="ID")
    assert covering_spans(words, [late, early]) == [early, early]


def test_no_spans_covers_nothing() -> None:
    assert covering_spans(split_words("nothing here"), []) == [None, None]


@settings(max_examples=100)
@given(_texts, st.lists(st.tuples(st.integers(0, 200), st.integers(1, 20)), max_size=8))
def test_covering_matches_brute_force(text: str, raw: list[tuple[int, int]]) -> None:
    words = split_words(text)
    spans = [Span(start=start, end=start + length) for start, length in raw]
    expected = [
        min(
            (s for s in spans if s.start < w.end and w.start < s.end),
            key=lambda s: s.start,
            default=None,
        )
        for w in words
    ]
    got = covering_spans(words, spans)
    assert [None if s is None else s.start for s in got] == [
        None if s is None else s.start for s in expected
    ]
