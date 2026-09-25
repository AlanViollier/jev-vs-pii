"""Word splitting keeps exact offsets; gold labelling marks words that touch a gold span."""

from __future__ import annotations

import unicodedata

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pii_bench.schema import Span
from pii_bench.words import gold_word_labels, split_words

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


def test_word_is_positive_when_it_overlaps_any_gold_span() -> None:
    text = "Send it to Marie Dupont at Lyon today."
    words = split_words(text)
    marie = text.index("Marie")
    lyon = text.index("Lyon")
    # the Lyon span covers only "yo": a partial overlap still makes the word positive
    gold = [Span(start=marie, end=marie + len("Marie Dupont")), Span(start=lyon + 1, end=lyon + 3)]
    labels = gold_word_labels(words, gold)
    assert len(labels) == len(words)
    assert [w.text for w, positive in zip(words, labels, strict=True) if positive] == [
        "Marie",
        "Dupont",
        "Lyon",
    ]


def test_span_touching_a_word_edge_does_not_overlap_it() -> None:
    words = split_words("ab cd")
    assert gold_word_labels(words, [Span(start=2, end=3)]) == [False, False]


def test_no_gold_means_no_positive_words() -> None:
    assert gold_word_labels(split_words("nothing here"), []) == [False, False]
