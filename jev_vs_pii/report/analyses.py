"""Checks on stored runs: free to rerun, never part of the headline rows.

`context_position`: whether Jev answers worse for questions past its documented context.
`answered_by_both`: two lanes compared on only the docs both of them answered.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import NamedTuple

from jev_vs_pii.lanes.designs import DESIGNS, Question
from jev_vs_pii.lanes.jev import batches, estimated_tokens, question_json, state_for
from jev_vs_pii.metrics.calibration import brier
from jev_vs_pii.metrics.spans import DocCounts, scores_from_counts
from jev_vs_pii.schema import Doc, LaneRun, ResultRow, SpanScores
from jev_vs_pii.words import covering_spans, split_words

## Jev's documented context, state plus questions; calls here are packed past it.
DOCUMENTED_CONTEXT_TOKENS = 32_000


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
        A `decision_<design>:jev` run.
    docs:
        The split's gold docs.
    limit:
        Where "past the context" starts, in tokens.

    Returns
    -------
    tuple[PositionBucket, PositionBucket]
        Before the limit, past it. A bucket with no words has no Brier score.
    """
    design = DESIGNS[lane_run.lane.id.partition(":")[0].removeprefix("decision_")]
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
            ## A word a design never asks about has no position, and no answer to judge.
            if i not in position:
                continue
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
    positions: Sequence[tuple[str, str, tuple[PositionBucket, PositionBucket]]],
    answered: Sequence[tuple[str, str, str, AnsweredByBoth]],
) -> str:
    """The checks as one Markdown section, appended to results.md."""
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
        "## Checks",
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
