"""Decoders turn word scores into well-formed spans; the simple cases of each one agree with threshold."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from pii_bench.decode import (
    Closing,
    DecodeParams,
    Hysteresis,
    Threshold,
    Viterbi,
    closing_mask,
    decode,
    hysteresis_mask,
    mask_to_spans,
    threshold_mask,
    viterbi_mask,
)
from pii_bench.schema import Word, WordScore

_probs = st.floats(min_value=0.0, max_value=1.0)
_score_lists = st.lists(st.builds(WordScore, p_pii=_probs), max_size=40)
_params = st.one_of(
    st.builds(Threshold, cutoff=_probs),
    st.builds(Closing, cutoff=_probs, gap=st.integers(0, 3)),
    st.builds(Viterbi, switch_cost=st.floats(0.0, 5.0)),
    st.tuples(_probs, _probs).map(lambda pair: Hysteresis(high=max(pair), low=min(pair))),
)


def _words(n: int) -> list[Word]:
    """`n` one-letter words separated by single spaces: word i sits at 2i."""
    return [Word(text="w", start=2 * i, end=2 * i + 1) for i in range(n)]


def _scores(*probs: float) -> list[WordScore]:
    return [WordScore(p_pii=p) for p in probs]


@settings(max_examples=100)
@given(_score_lists, _params)
def test_spans_are_sorted_disjoint_and_on_word_boundaries(
    scores: list[WordScore], params: DecodeParams
) -> None:
    words = _words(len(scores))
    spans = decode(words, scores, params)
    starts = {w.start for w in words}
    ends = {w.end for w in words}
    for span in spans:
        assert span.start in starts
        assert span.end in ends
        assert span.score is not None
    for left, right in zip(spans, spans[1:], strict=False):
        assert left.end < right.start


@settings(max_examples=100)
@given(_score_lists, _probs)
def test_hysteresis_with_equal_cutoffs_is_threshold(scores: list[WordScore], cutoff: float) -> None:
    assert hysteresis_mask(scores, Hysteresis(high=cutoff, low=cutoff)) == threshold_mask(
        scores, Threshold(cutoff=cutoff)
    )


@settings(max_examples=100)
@given(_score_lists, _probs)
def test_closing_without_gap_is_threshold(scores: list[WordScore], cutoff: float) -> None:
    assert closing_mask(scores, Closing(cutoff=cutoff, gap=0)) == threshold_mask(
        scores, Threshold(cutoff=cutoff)
    )


@settings(max_examples=100)
@given(_score_lists)
def test_free_switching_viterbi_is_threshold_at_half(scores: list[WordScore]) -> None:
    assert viterbi_mask(scores, Viterbi(switch_cost=0.0)) == threshold_mask(
        scores, Threshold(cutoff=0.5)
    )


@settings(max_examples=100)
@given(_score_lists, _probs, _probs)
def test_higher_cutoff_never_adds_words(scores: list[WordScore], a: float, b: float) -> None:
    loose = threshold_mask(scores, Threshold(cutoff=min(a, b)))
    strict = threshold_mask(scores, Threshold(cutoff=max(a, b)))
    assert all(
        loose_word or not strict_word for loose_word, strict_word in zip(loose, strict, strict=True)
    )


def test_hysteresis_grows_from_a_strong_seed_only() -> None:
    scores = _scores(0.4, 0.9, 0.4, 0.1, 0.4, 0.4)
    assert hysteresis_mask(scores, Hysteresis(high=0.8, low=0.3)) == [
        True,
        True,
        True,
        False,
        False,
        False,
    ]


def test_closing_bridges_short_holes_between_positives_only() -> None:
    scores = _scores(0.1, 0.9, 0.2, 0.9, 0.2, 0.2, 0.9, 0.1)
    assert closing_mask(scores, Closing(cutoff=0.5, gap=1)) == [
        False,
        True,
        True,
        True,
        False,
        False,
        True,
        False,
    ]


def test_viterbi_absorbs_a_short_dip_when_switching_is_expensive() -> None:
    scores = _scores(0.9, 0.9, 0.4, 0.9, 0.1)
    assert viterbi_mask(scores, Viterbi(switch_cost=0.0)) == [True, True, False, True, False]
    assert viterbi_mask(scores, Viterbi(switch_cost=2.0)) == [True, True, True, True, False]


def test_viterbi_handles_certain_scores() -> None:
    assert viterbi_mask(_scores(0.0, 1.0, 1.0, 0.0), Viterbi(switch_cost=1.0)) == [
        False,
        True,
        True,
        False,
    ]


def test_adjacent_positive_words_merge_into_one_scored_span() -> None:
    words = _words(4)
    spans = mask_to_spans(words, _scores(0.1, 0.8, 0.6, 0.1), [False, True, True, False])
    assert [(s.start, s.end) for s in spans] == [(2, 5)]
    assert spans[0].score == pytest.approx(0.7)
    assert spans[0].label is None


def test_low_p_continue_splits_a_run() -> None:
    scores = [
        WordScore(p_pii=0.9),
        WordScore(p_pii=0.9, p_continue=0.9),
        WordScore(p_pii=0.9, p_continue=0.1),
    ]
    spans = mask_to_spans(_words(3), scores, [True, True, True])
    assert [(s.start, s.end) for s in spans] == [(0, 3), (4, 5)]


def test_type_change_splits_a_run_and_labels_each_span() -> None:
    scores = [
        WordScore(p_pii=0.9, label_probs={"PERSON": 0.8, "LOCATION": 0.2}),
        WordScore(p_pii=0.9, label_probs={"PERSON": 0.7, "LOCATION": 0.3}),
        WordScore(p_pii=0.9, label_probs={"PERSON": 0.1, "LOCATION": 0.9}),
    ]
    spans = mask_to_spans(_words(3), scores, [True, True, True])
    assert [(s.start, s.end, s.label) for s in spans] == [(0, 3, "PERSON"), (4, 5, "LOCATION")]


def test_no_words_no_spans() -> None:
    assert decode([], [], Threshold()) == []


def test_mismatched_lengths_fail_loudly() -> None:
    with pytest.raises(ValueError):
        decode(_words(2), _scores(0.9), Threshold())


def test_hysteresis_rejects_low_above_high() -> None:
    with pytest.raises(ValidationError):
        Hysteresis(high=0.3, low=0.6)
