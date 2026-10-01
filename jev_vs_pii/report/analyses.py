"""Checks and what-ifs on stored runs: free to rerun, never part of the headline rows.

`stop_word_skip`: what Jev's stored scores give if common function words are never asked about.
`context_position`: whether Jev answers worse for questions past its documented context.
`answered_by_both`: two lanes compared on only the docs both of them answered.
"""

from __future__ import annotations

import json
from collections.abc import Collection, Sequence
from typing import NamedTuple

from jev_vs_pii.decode import DecodeParams, decode
from jev_vs_pii.lanes.jev import batches, estimated_tokens, question_json, state_for
from jev_vs_pii.lanes.jev_designs import DESIGNS, Question
from jev_vs_pii.metrics.calibration import brier
from jev_vs_pii.metrics.spans import DocCounts, doc_counts, scores_from_counts
from jev_vs_pii.schema import Doc, LaneRun, ResultRow, SpanScores
from jev_vs_pii.words import covering_spans, split_words

## Jev's documented context, state plus questions; calls here are packed past it.
DOCUMENTED_CONTEXT_TOKENS = 32_000


class StopWordSkip(NamedTuple):
    """Word-level scores before and after skipping stop words, and what the skip costs."""

    before: SpanScores
    after: SpanScores
    questions_kept: float
    gold_words_skipped: float


class PositionBucket(NamedTuple):
    """Jev's word answers asked within one stretch of their call."""

    words: int
    brier: float | None
    gold_share: float | None


class AnsweredByBoth(NamedTuple):
    """Two lanes scored on the docs neither failed."""

    docs: int
    a: SpanScores
    b: SpanScores


def stop_word_skip(
    lane_run: LaneRun, docs: Sequence[Doc], decoder: DecodeParams, stop_words: Collection[str]
) -> StopWordSkip:
    """Rescore a per-word run as if words in `stop_words` had never been asked about.

    A skipped word scores 0, so it is never masked. Nothing is called again: this reads
    the stored scores, which is why it stays a what-if and never a headline row.

    Parameters
    ----------
    lane_run:
        A run whose predictions carry word scores.
    docs:
        The split's gold docs.
    decoder:
        The lane's headline decoder, used before and after.
    stop_words:
        Lowercase words never to ask about.

    Returns
    -------
    StopWordSkip
        Scores before and after, the share of questions still asked, and the share of
        gold words that are stop words (those are always missed after the skip).
    """
    by_id = {doc.id: doc for doc in docs}
    before: list[DocCounts] = []
    after: list[DocCounts] = []
    asked = kept = gold_total = gold_skipped = 0
    for prediction in lane_run.predictions:
        if prediction.word_scores is None:
            raise ValueError(f"{lane_run.lane.id}: no word scores to skip words in")
        doc = by_id[prediction.doc_id]
        words = split_words(doc.text)
        skip = [word.text.lower() in stop_words for word in words]
        gold = [span is not None for span in covering_spans(words, doc.gold)]
        skipped_scores = [
            score.model_copy(update={"p_pii": 0.0}) if skipped else score
            for score, skipped in zip(prediction.word_scores, skip, strict=True)
        ]
        before.append(doc_counts(doc, decode(words, prediction.word_scores, decoder), "word"))
        after.append(doc_counts(doc, decode(words, skipped_scores, decoder), "word"))
        asked += len(words)
        kept += skip.count(False)
        gold_total += sum(gold)
        gold_skipped += sum(
            is_gold and skipped for is_gold, skipped in zip(gold, skip, strict=True)
        )
    return StopWordSkip(
        before=scores_from_counts(before),
        after=scores_from_counts(after),
        questions_kept=kept / asked if asked else 0.0,
        gold_words_skipped=gold_skipped / gold_total if gold_total else 0.0,
    )


def context_position(
    lane_run: LaneRun, docs: Sequence[Doc], limit: int = DOCUMENTED_CONTEXT_TOKENS
) -> tuple[PositionBucket, PositionBucket]:
    """Brier score of a Jev run's word answers asked before vs past `limit` tokens into their call.

    The calls are rebuilt exactly as the lane sent them. A word's position is the end of
    its first question, counting the state; positions use the lane's size estimate,
    rescaled per doc so its calls add up to the input tokens actually billed.

    Parameters
    ----------
    lane_run:
        A `jev_<design>` run.
    docs:
        The split's gold docs.
    limit:
        Where "past the context" starts, in tokens.

    Returns
    -------
    tuple[PositionBucket, PositionBucket]
        Before the limit, past it. A bucket with no words has no Brier score.
    """
    design = DESIGNS[lane_run.lane.id.removeprefix("jev_")]
    by_id = {doc.id: doc for doc in docs}
    sides: dict[bool, tuple[list[float], list[bool]]] = {False: ([], []), True: ([], [])}
    for prediction in lane_run.predictions:
        doc = by_id[prediction.doc_id]
        words = split_words(doc.text)
        questions: dict[str, Question] = {}
        for i in range(len(words)):
            questions.update(design.ask(doc, words, i))
        state = state_for(doc)
        state_tokens = estimated_tokens(json.dumps(state))
        sizes = {key: estimated_tokens(question_json(key, q)) for key, q in questions.items()}
        calls = batches(state, questions)
        estimate = sum(state_tokens + sum(sizes[key] for key in call) for call in calls)
        billed = prediction.usage.input_tokens
        scale = billed / estimate if billed and estimate else 1.0
        position: dict[int, float] = {}
        for call in calls:
            reached = state_tokens
            for key in call:
                reached += sizes[key]
                ## Every design's keys are one letter, then the index of the word asked about.
                position.setdefault(int(key[1:]), reached * scale)
        gold = covering_spans(words, doc.gold)
        for i, score in enumerate(prediction.word_scores or ()):
            probs, labels = sides[position[i] > limit]
            probs.append(score.p_pii)
            labels.append(gold[i] is not None)
    return _bucket(*sides[False]), _bucket(*sides[True])


def answered_by_both(a: ResultRow, b: ResultRow) -> AnsweredByBoth:
    """Word-level scores of two rows on the docs where neither lane's answer failed."""
    theirs = {doc.doc_id: doc for doc in b.per_doc}
    shared = [
        d for d in a.per_doc if d.doc_id in theirs and not (d.failed or theirs[d.doc_id].failed)
    ]
    return AnsweredByBoth(
        docs=len(shared),
        a=scores_from_counts(DocCounts(d.tp, d.fp, d.fn) for d in shared),
        b=scores_from_counts(
            DocCounts(theirs[d.doc_id].tp, theirs[d.doc_id].fp, theirs[d.doc_id].fn) for d in shared
        ),
    )


def analyses_markdown(
    skips: Sequence[tuple[str, str, StopWordSkip]],
    positions: Sequence[tuple[str, str, tuple[PositionBucket, PositionBucket]]],
    answered: Sequence[tuple[str, str, str, AnsweredByBoth]],
) -> str:
    """The three checks as one Markdown section, appended to results.md."""
    skip_table = [
        "| lane | dataset | questions kept | gold words that are stop words "
        "| F2 before → after | P before → after | R before → after | F1 before → after |",
        "|---|---|---|---|---|---|---|---|",
        *(
            f"| {lane} | {dataset} | {s.questions_kept:.0%} | {s.gold_words_skipped:.1%} "
            f"| {s.before.f2:.3f} → {s.after.f2:.3f} "
            f"| {s.before.precision:.3f} → {s.after.precision:.3f} "
            f"| {s.before.recall:.3f} → {s.after.recall:.3f} | {s.before.f1:.3f} → {s.after.f1:.3f} |"
            for lane, dataset, s in skips
        ),
    ]
    position_table = [
        "| lane | dataset | words before | Brier before | PII share before "
        "| words past | Brier past | PII share past |",
        "|---|---|---|---|---|---|---|---|",
        *(
            f"| {lane} | {dataset} | {early.words:,} | {_maybe(early.brier)} "
            f"| {_maybe(early.gold_share)} | {late.words:,} | {_maybe(late.brier)} "
            f"| {_maybe(late.gold_share)} |"
            for lane, dataset, (early, late) in positions
        ),
    ]
    answered_table = [
        "| dataset | lane A | lane B | docs | F2 A | F2 B | P A / B | R A / B |",
        "|---|---|---|---|---|---|---|---|",
        *(
            f"| {dataset} | {lane_a} | {lane_b} | {r.docs} | {r.a.f2:.3f} | {r.b.f2:.3f} "
            f"| {r.a.precision:.3f} / {r.b.precision:.3f} | {r.a.recall:.3f} / {r.b.recall:.3f} |"
            for dataset, lane_a, lane_b, r in answered
        ),
    ]
    blocks = [
        "## Checks and what-ifs",
        "### What-if: Jev never asked about stop words "
        "(spaCy's English list; stored scores, same threshold)",
        "\n".join(skip_table),
        f"### Check: Jev's answers before vs past its documented "
        f"{DOCUMENTED_CONTEXT_TOKENS:,}-token context",
        "\n".join(position_table),
        "### Check: two lanes on only the docs both answered",
        "\n".join(answered_table),
    ]
    return "\n\n".join(blocks) + "\n"


def _bucket(probs: list[float], labels: list[bool]) -> PositionBucket:
    if not probs:
        return PositionBucket(words=0, brier=None, gold_share=None)
    return PositionBucket(
        words=len(probs), brier=brier(probs, labels), gold_share=sum(labels) / len(labels)
    )


def _maybe(value: float | None) -> str:
    return "–" if value is None else f"{value:.3f}"
