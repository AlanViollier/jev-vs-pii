"""Split text into words with character offsets, and label words against gold spans."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence

from pii_bench.schema import Span, Word

_TOKEN = re.compile(r"\S+")


def split_words(text: str) -> list[Word]:
    """Split `text` on whitespace and trim edge punctuation, keeping character offsets.

    Parameters
    ----------
    text:
        Source document text.

    Returns
    -------
    list[Word]
        Words in order; `text[w.start:w.end] == w.text` for every word.
        Tokens made only of punctuation are dropped. Symbols (`+`, `$`, `€`, `#`) are
        kept because they are often part of the PII itself. Known edge cases: a
        leading hyphen is trimmed (`-5` -> `5`), so is an abbreviation's last stop
        (`U.S.` -> `U.S`), and a lone symbol is its own word (`a + b` -> `+`).
        Gold labels match by overlap, so trimming never changes a word's label.
    """
    words = []
    for match in _TOKEN.finditer(text):
        start, end = match.span()
        while start < end and _is_punct(text[start]):
            start += 1
        while end > start and _is_punct(text[end - 1]):
            end -= 1
        if start < end:
            words.append(Word(text=text[start:end], start=start, end=end))
    return words


def gold_word_labels(words: Sequence[Word], gold: Sequence[Span]) -> list[bool]:
    """Mark each word positive when it overlaps any gold span.

    Parameters
    ----------
    words:
        Output of `split_words` on the doc text.
    gold:
        Gold spans of the same doc.

    Returns
    -------
    list[bool]
        One flag per word.
    """
    return [any(w.start < s.end and s.start < w.end for s in gold) for w in words]


def _is_punct(char: str) -> bool:
    """Unicode punctuation (categories P*): quotes, brackets, dashes, stops."""
    return unicodedata.category(char).startswith("P")
