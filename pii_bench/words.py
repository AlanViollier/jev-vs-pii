"""Split text into words with character offsets; map spans and scores onto those words."""

from __future__ import annotations

import bisect
import re
import unicodedata
from collections.abc import Sequence

from pii_bench.schema import Span, Word, WordScore

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


def covering_spans(words: Sequence[Word], spans: Sequence[Span]) -> list[Span | None]:
    """Find, for each word, the span that overlaps it.

    Parameters
    ----------
    words:
        Output of `split_words` on the doc text.
    spans:
        Gold or predicted spans of the same doc, any order.

    Returns
    -------
    list[Span | None]
        One entry per word: the earliest-starting span sharing a character with it,
        or None. A word is positive exactly when its entry is not None.
    """
    covering: list[Span | None] = [None] * len(words)
    for span in sorted(spans, key=lambda span: span.start, reverse=True):
        first = bisect.bisect_right(words, span.start, key=lambda word: word.end)
        for i in range(first, len(words)):
            if words[i].start >= span.end:
                break
            covering[i] = span
    return covering


def _is_punct(char: str) -> bool:
    """Unicode punctuation (categories P*): quotes, brackets, dashes, stops."""
    return unicodedata.category(char).startswith("P")


def word_scores_from(words: Sequence[Word], scored: Sequence[Span]) -> tuple[WordScore, ...]:
    """Per-word probability from scored ranges (model tokens or spans): the best one touching it.

    Parameters
    ----------
    words:
        Words of the doc, from `split_words`.
    scored:
        Character ranges with a `score` in [0, 1]; may overlap, any order.

    Returns
    -------
    tuple[WordScore, ...]
        One score per word; 0 for a word no range touches.
    """
    best = [0.0] * len(words)
    for span in scored:
        first = bisect.bisect_right(words, span.start, key=lambda word: word.end)
        for i in range(first, len(words)):
            if words[i].start >= span.end:
                break
            best[i] = max(best[i], span.score or 0.0)
    return tuple(WordScore(p_pii=p) for p in best)
