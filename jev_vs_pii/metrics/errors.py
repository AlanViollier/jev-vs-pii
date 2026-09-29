"""What a lane gets wrong, as text: the gold strings it leaks and the strings it masks for nothing."""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from jev_vs_pii.schema import Doc, Span
from jev_vs_pii.words import covering_spans, split_words


def top_errors(
    docs: Sequence[Doc], preds: Sequence[Sequence[Span]], n: int = 15
) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    """Most frequent leaked gold strings and false-alarm strings, case-folded.

    Parameters
    ----------
    docs:
        Gold docs. Only call this on data whose text may be shown (TAB).
    preds:
        Predicted spans per doc, same order as `docs`.
    n:
        How many of each to keep.

    Returns
    -------
    tuple[list[tuple[str, int]], list[tuple[str, int]]]
        (gold spans with at least one unmasked word, predicted spans that touch no gold
        word), each as (text, count), most frequent first.
    """
    missed: Counter[str] = Counter()
    false_alarms: Counter[str] = Counter()
    for doc, pred in zip(docs, preds, strict=True):
        words = split_words(doc.text)
        guessed = covering_spans(words, pred)
        gold = covering_spans(words, doc.gold)
        for span in doc.gold:
            if any(guessed[i] is None for i, g in enumerate(gold) if g is span):
                missed[_text(doc, span)] += 1
        for span in pred:
            covered = [gold[i] for i, g in enumerate(guessed) if g is span]
            if covered and all(g is None for g in covered):
                false_alarms[_text(doc, span)] += 1
    return missed.most_common(n), false_alarms.most_common(n)


def _text(doc: Doc, span: Span) -> str:
    return " ".join(doc.text[span.start : span.end].split()).lower()
