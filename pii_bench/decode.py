"""Turn per-word scores into spans. Pure code on cached scores, so every decoder is free to compare."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from pii_bench.schema import Span, Word, WordScore


class Threshold(BaseModel):
    """Each word alone: positive when `p_pii >= cutoff`."""

    kind: Literal["threshold"] = "threshold"
    cutoff: float = 0.5


class Hysteresis(BaseModel):
    """A span needs one word `>= high` to start, then grows while neighbours stay `>= low`."""

    kind: Literal["hysteresis"] = "hysteresis"
    high: float = 0.6
    low: float = 0.3


class Closing(BaseModel):
    """Threshold, then bridge holes of at most `gap` words between positive words."""

    kind: Literal["closing"] = "closing"
    cutoff: float = 0.5
    gap: int = 1


class Viterbi(BaseModel):
    """Best in/out labelling with a cost per switch; uses `p_continue` for joins when present."""

    kind: Literal["viterbi"] = "viterbi"
    switch_cost: float = 0.5


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
    raise NotImplementedError


def threshold_mask(scores: Sequence[WordScore], params: Threshold) -> list[bool]:
    """Positive words under a single cutoff."""
    raise NotImplementedError


def hysteresis_mask(scores: Sequence[WordScore], params: Hysteresis) -> list[bool]:
    """Positive words under two cutoffs: seed high, grow low."""
    raise NotImplementedError


def closing_mask(scores: Sequence[WordScore], params: Closing) -> list[bool]:
    """Positive words under a cutoff, with short holes bridged."""
    raise NotImplementedError


def viterbi_mask(scores: Sequence[WordScore], params: Viterbi) -> list[bool]:
    """Most likely in/out path given each word's score and a switch penalty."""
    raise NotImplementedError


def mask_to_spans(
    words: Sequence[Word], scores: Sequence[WordScore], mask: Sequence[bool]
) -> list[Span]:
    """Merge runs of positive words into spans; label and score each span from its words."""
    raise NotImplementedError
