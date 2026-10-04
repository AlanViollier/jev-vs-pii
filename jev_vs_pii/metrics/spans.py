"""Precision / recall / F1 / F2 over words (the headline) or exact spans, typed or not."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from typing import NamedTuple

from jev_vs_pii.schema import Doc, Hits, MatchMode, Span, SpanScores
from jev_vs_pii.words import covering_spans, split_words


class DocCounts(NamedTuple):
    """True positives, false positives and false negatives on one doc."""

    tp: int
    fp: int
    fn: int


def score_spans(
    docs: Sequence[Doc],
    preds: Sequence[Sequence[Span]],
    mode: MatchMode,
    typed: bool = False,
) -> SpanScores:
    """Score predicted spans against gold, micro-averaged over docs.

    Parameters
    ----------
    docs:
        Gold docs.
    preds:
        Predicted spans per doc, same order as `docs`.
    mode:
        `word`: a word is gold when a gold span overlaps it, predicted when a predicted
        span does. `exact`: a span counts only with identical offsets.
    typed:
        When true a match also needs the same coarse label.

    Returns
    -------
    SpanScores
        Counts plus P / R / F1 / F2 (F2 weights recall: a leak costs more than an over-mask).
    """
    return scores_from_counts(
        doc_counts(doc, pred, mode, typed) for doc, pred in zip(docs, preds, strict=True)
    )


def doc_counts(doc: Doc, pred: Sequence[Span], mode: MatchMode, typed: bool = False) -> DocCounts:
    """Count one doc's matches; summing these is what the bootstrap resamples.

    Parameters
    ----------
    doc:
        The gold doc.
    pred:
        Spans a lane predicted on it.
    mode:
        `word` or `exact`, as in `score_spans`.
    typed:
        When true a match also needs the same coarse label.

    Returns
    -------
    DocCounts
        tp / fp / fn in words or in spans, per `mode`.
    """
    if mode == "exact":
        gold_keys = {_exact_key(span, typed) for span in doc.gold}
        pred_keys = {_exact_key(span, typed) for span in pred}
        return DocCounts(
            tp=len(gold_keys & pred_keys),
            fp=len(pred_keys - gold_keys),
            fn=len(gold_keys - pred_keys),
        )
    tp = fp = fn = 0
    for gold, guess in word_pairs(doc, pred):
        hit = gold is not None and guess is not None and (not typed or gold.label == guess.label)
        tp += hit
        fp += guess is not None and not hit
        fn += gold is not None and not hit
    return DocCounts(tp=tp, fp=fp, fn=fn)


def scores_from_counts(counts: Iterable[DocCounts]) -> SpanScores:
    """Sum per-doc counts and derive the scores; empty denominators score 0.

    Parameters
    ----------
    counts:
        One `DocCounts` per doc (repeats allowed, as in a bootstrap resample).

    Returns
    -------
    SpanScores
        Micro-averaged counts and scores.
    """
    tp = fp = fn = 0
    for doc in counts:
        tp += doc.tp
        fp += doc.fp
        fn += doc.fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return SpanScores(
        tp=tp,
        fp=fp,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=_f_beta(precision, recall, beta=1.0),
        f2=_f_beta(precision, recall, beta=2.0),
    )


def gold_hits_by(
    docs: Sequence[Doc], preds: Sequence[Sequence[Span]], key: Callable[[Span], str | None]
) -> dict[str, Hits]:
    """Word-level recall counts per group of gold spans: where each method leaks.

    Uses gold labels only, so it works for lanes that predict no types.

    Parameters
    ----------
    docs:
        Gold docs.
    preds:
        Predicted spans per doc, same order as `docs`.
    key:
        Group of a gold span, e.g. its coarse `label` or its dataset `detail`; None skips it.

    Returns
    -------
    dict[str, Hits]
        Group -> (gold words covered by some prediction, gold words).
    """
    hits: Counter[str] = Counter()
    total: Counter[str] = Counter()
    for doc, pred in zip(docs, preds, strict=True):
        for gold, guess in word_pairs(doc, pred):
            group = key(gold) if gold is not None else None
            if group is None:
                continue
            total[group] += 1
            hits[group] += guess is not None
    return {group: (hits[group], count) for group, count in total.items()}


def predicted_hits_by_type(docs: Sequence[Doc], preds: Sequence[Sequence[Span]]) -> dict[str, Hits]:
    """Word-level precision counts per predicted type: what each type a lane claims is worth.

    Parameters
    ----------
    docs:
        Gold docs.
    preds:
        Predicted spans per doc; spans without a label are skipped.

    Returns
    -------
    dict[str, Hits]
        Predicted label -> (predicted words that are gold PII of any type, predicted words).
    """
    hits: Counter[str] = Counter()
    total: Counter[str] = Counter()
    for doc, pred in zip(docs, preds, strict=True):
        for gold, guess in word_pairs(doc, pred):
            if guess is None or guess.label is None:
                continue
            total[guess.label] += 1
            hits[guess.label] += gold is not None
    return {label: (hits[label], count) for label, count in total.items()}


def cleared_hits(docs: Sequence[Doc], preds: Sequence[Sequence[Span]]) -> Hits:
    """How much of what the annotator left in clear a lane masked anyway: context over-masking.

    Parameters
    ----------
    docs:
        Gold docs carrying `cleared` entities (TAB's NO_MASK).
    preds:
        Predicted spans per doc, same order as `docs`.

    Returns
    -------
    Hits
        (masked words inside cleared entities, words inside cleared entities), leaving out
        words that some gold span also covers.
    """
    masked = total = 0
    for doc, pred in zip(docs, preds, strict=True):
        words = split_words(doc.text)
        for gold, cleared, guess in zip(
            covering_spans(words, doc.gold),
            covering_spans(words, doc.cleared),
            covering_spans(words, pred),
            strict=True,
        ):
            if cleared is None or gold is not None:
                continue
            total += 1
            masked += guess is not None
    return masked, total


def share(hits: Hits | None) -> float | None:
    """Hits over total, or None when there is nothing to count."""
    return hits[0] / hits[1] if hits and hits[1] else None


def word_pairs(doc: Doc, pred: Sequence[Span]) -> list[tuple[Span | None, Span | None]]:
    """For each word of the doc: the gold span and the predicted span covering it, if any."""
    words = split_words(doc.text)
    return list(zip(covering_spans(words, doc.gold), covering_spans(words, pred), strict=True))


def _exact_key(span: Span, typed: bool) -> tuple[int, int, str | None]:
    return (span.start, span.end, span.label if typed else None)


def _f_beta(precision: float, recall: float, beta: float) -> float:
    weight = beta**2
    denominator = weight * precision + recall
    return (1 + weight) * precision * recall / denominator if denominator else 0.0
