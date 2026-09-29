"""Paired comparison, threshold curve, error strings and the cost/quality frontier on hand-made cases."""

from __future__ import annotations

import pytest

from pii_bench.metrics.bootstrap import paired_f2_diff
from pii_bench.metrics.curve import threshold_curve
from pii_bench.metrics.errors import top_errors
from pii_bench.metrics.spans import DocCounts
from pii_bench.schema import Doc, Span


def test_a_lane_against_itself_differs_by_nothing() -> None:
    counts = [DocCounts(3, 1, 1), DocCounts(0, 2, 4), DocCounts(5, 0, 0)]
    assert paired_f2_diff(counts, counts) == (0.0, 0.0, 0.0)


def test_a_lane_better_on_every_doc_has_an_interval_above_zero() -> None:
    better = [DocCounts(4, 0, 0)] * 30
    worse = [DocCounts(2, 1, 2)] * 30
    diff, low, high = paired_f2_diff(better, worse)
    assert diff > 0 and low > 0 and high >= low


def test_paired_comparison_needs_the_same_docs() -> None:
    with pytest.raises(ValueError, match="same docs"):
        paired_f2_diff([DocCounts(1, 0, 0)], [])


def test_threshold_curve_counts_words_at_or_above_each_cutoff() -> None:
    probs = [0.9, 0.6, 0.4, 0.1]
    labels = [True, False, True, False]
    low, high = threshold_curve(probs, labels, cutoffs=(0.4, 0.9))
    assert (low.cutoff, low.recall) == (0.4, 1.0)
    assert low.precision == pytest.approx(2 / 3)
    assert (high.precision, high.recall) == (1.0, 0.5)


def test_errors_name_leaked_gold_and_masks_that_touch_no_gold() -> None:
    text = "Mr Ivo Brandt met the Court in Oslo on Monday"
    gold = (
        Span(start=3, end=13, label="PERSON"),
        Span(start=31, end=35, label="LOCATION"),
    )
    doc = Doc(id="d", dataset="tab", split="test", text=text, gold=gold, subject="Ivo Brandt")
    pred = [Span(start=3, end=6), Span(start=22, end=27), Span(start=31, end=35)]
    missed, false_alarms = top_errors([doc], [pred])
    assert missed == [("ivo brandt", 1)]
    assert false_alarms == [("court", 1)]
