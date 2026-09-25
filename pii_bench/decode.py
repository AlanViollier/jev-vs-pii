"""Turn per-word scores into spans. Pure code on cached scores, so every decoder is free to compare."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, model_validator

from pii_bench.schema import Span, Word, WordScore

## Keeps -log finite for scores of exactly 0 or 1.
_EPS = 1e-9
## A word whose `p_continue` falls below this starts a new span.
_JOIN_CUTOFF = 0.5


class Threshold(BaseModel):
    """Each word alone: positive when `p_pii >= cutoff`."""

    kind: Literal["threshold"] = "threshold"
    cutoff: float = Field(default=0.5, ge=0.0, le=1.0)


class Hysteresis(BaseModel):
    """A span needs one word `>= high` to start, then grows while neighbours stay `>= low`."""

    kind: Literal["hysteresis"] = "hysteresis"
    high: float = Field(default=0.6, ge=0.0, le=1.0)
    low: float = Field(default=0.3, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _low_not_above_high(self) -> Self:
        if self.low > self.high:
            raise ValueError(f"low {self.low} must not exceed high {self.high}")
        return self


class Closing(BaseModel):
    """Threshold, then bridge holes of at most `gap` words between positive words."""

    kind: Literal["closing"] = "closing"
    cutoff: float = Field(default=0.5, ge=0.0, le=1.0)
    gap: int = Field(default=1, ge=0)


class Viterbi(BaseModel):
    """Cheapest in/out path: each word costs -log of the chosen side's probability, each switch `switch_cost`."""

    kind: Literal["viterbi"] = "viterbi"
    switch_cost: float = Field(default=0.5, ge=0.0)


DecodeParams = Annotated[Threshold | Hysteresis | Closing | Viterbi, Field(discriminator="kind")]


def decode(words: Sequence[Word], scores: Sequence[WordScore], params: DecodeParams) -> list[Span]:
    """Decode word scores into spans with the method `params` names.

    Parameters
    ----------
    words:
        Words of the doc, from `split_words`.
    scores:
        One score per word, same order.
    params:
        Which decoder, with its knobs.

    Returns
    -------
    list[Span]
        Non-overlapping spans in text order; score = mean `p_pii` of the words inside,
        label = most likely type when the scores carry `label_probs`.
    """
    if len(words) != len(scores):
        raise ValueError(f"{len(words)} words but {len(scores)} scores")
    match params:
        case Threshold():
            mask = threshold_mask(scores, params)
        case Hysteresis():
            mask = hysteresis_mask(scores, params)
        case Closing():
            mask = closing_mask(scores, params)
        case Viterbi():
            mask = viterbi_mask(scores, params)
    return mask_to_spans(words, scores, mask)


def threshold_mask(scores: Sequence[WordScore], params: Threshold) -> list[bool]:
    """Positive words under a single cutoff."""
    return [score.p_pii >= params.cutoff for score in scores]


def hysteresis_mask(scores: Sequence[WordScore], params: Hysteresis) -> list[bool]:
    """Positive words under two cutoffs: seed high, grow low."""
    mask = [False] * len(scores)
    for start, end in _runs([score.p_pii >= params.low for score in scores]):
        if any(score.p_pii >= params.high for score in scores[start:end]):
            mask[start:end] = [True] * (end - start)
    return mask


def closing_mask(scores: Sequence[WordScore], params: Closing) -> list[bool]:
    """Positive words under a cutoff, with short holes bridged."""
    mask = threshold_mask(scores, Threshold(cutoff=params.cutoff))
    holes = _runs([not positive for positive in mask])
    for start, end in holes:
        if start > 0 and end < len(mask) and end - start <= params.gap:
            mask[start:end] = [True] * (end - start)
    return mask


def viterbi_mask(scores: Sequence[WordScore], params: Viterbi) -> list[bool]:
    """Most likely in/out path given each word's score and a switch penalty."""
    ## Cheapest path so far ending out / in, and where each came from. Ties go in, like threshold's >=.
    cost_out, cost_in = 0.0, 0.0
    came_from_in: list[tuple[bool, bool]] = []
    for score in scores:
        p_in = min(max(score.p_pii, _EPS), 1 - _EPS)
        out_via_in = cost_in + params.switch_cost <= cost_out
        in_via_in = cost_in <= cost_out + params.switch_cost
        came_from_in.append((out_via_in, in_via_in))
        cost_out, cost_in = (
            min(cost_out, cost_in + params.switch_cost) - math.log(1 - p_in),
            min(cost_in, cost_out + params.switch_cost) - math.log(p_in),
        )
    inside = cost_in <= cost_out
    path = []
    for out_via_in, in_via_in in reversed(came_from_in):
        path.append(inside)
        inside = in_via_in if inside else out_via_in
    return path[::-1]


def mask_to_spans(
    words: Sequence[Word], scores: Sequence[WordScore], mask: Sequence[bool]
) -> list[Span]:
    """Merge runs of positive words into spans; label and score each span from its words.

    A run also breaks where a word's `p_continue` is low or its most likely type changes,
    so BIO and typed lanes get their boundaries whatever decoder made the mask.
    """
    spans = []
    for start, end in _runs(mask):
        for piece_start, piece_end in _split_run(scores, start, end):
            inside = scores[piece_start:piece_end]
            spans.append(
                Span(
                    start=words[piece_start].start,
                    end=words[piece_end - 1].end,
                    label=_span_label(inside),
                    score=sum(score.p_pii for score in inside) / len(inside),
                )
            )
    return spans


def _runs(mask: Sequence[bool]) -> list[tuple[int, int]]:
    """Half-open index ranges of consecutive True values."""
    runs = []
    start = None
    for i, positive in enumerate([*mask, False]):
        if positive and start is None:
            start = i
        elif not positive and start is not None:
            runs.append((start, i))
            start = None
    return runs


def _split_run(scores: Sequence[WordScore], start: int, end: int) -> list[tuple[int, int]]:
    """Cut one positive run where a word doesn't continue the previous one."""
    cuts = [i for i in range(start + 1, end) if _starts_new_item(scores[i - 1], scores[i])]
    bounds = [start, *cuts, end]
    return list(zip(bounds, bounds[1:], strict=False))


def _starts_new_item(previous: WordScore, word: WordScore) -> bool:
    if word.p_continue is not None and word.p_continue < _JOIN_CUTOFF:
        return True
    return _top_label(word) != _top_label(previous)


def _top_label(score: WordScore) -> str | None:
    if score.label_probs is None:
        return None
    return max(score.label_probs, key=score.label_probs.__getitem__)


def _span_label(scores: Sequence[WordScore]) -> str | None:
    """Type with the highest summed probability across the span's words."""
    totals: dict[str, float] = {}
    for score in scores:
        for label, prob in (score.label_probs or {}).items():
            totals[label] = totals.get(label, 0.0) + prob
    return max(totals, key=totals.__getitem__) if totals else None
