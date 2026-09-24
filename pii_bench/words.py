"""Split text into words with character offsets, and label words against gold spans."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.schema import Span, Word


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
    """
    raise NotImplementedError


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
    raise NotImplementedError
