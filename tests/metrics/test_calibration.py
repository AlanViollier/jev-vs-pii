"""Calibration on hand-computed cases: a perfect forecaster scores 0, a confident liar scores high."""

from __future__ import annotations

import pytest

from jev_vs_pii.metrics.calibration import brier, ece, reliability_bins


def test_brier_hand_computed() -> None:
    assert brier([0.9, 0.2, 0.5], [True, False, True]) == pytest.approx((0.01 + 0.04 + 0.25) / 3)


def test_perfectly_calibrated_bins_have_zero_ece() -> None:
    probs = [0.25] * 4 + [0.75] * 4
    labels = [True, False, False, False, True, True, True, False]
    assert ece(probs, labels, n_bins=4) == pytest.approx(0.0)


def test_confident_and_wrong_has_high_ece() -> None:
    assert ece([0.95] * 10, [False] * 10) == pytest.approx(0.95)


def test_bins_skip_empty_and_put_one_in_the_last_bin() -> None:
    bins = reliability_bins([0.05, 0.1, 1.0, 0.95], [False, True, True, True], n_bins=10)
    assert [(b.low, b.count) for b in bins] == [(0.0, 1), (0.1, 1), (0.9, 2)]
    assert bins[-1].mean_confidence == pytest.approx(0.975)
    assert bins[-1].accuracy == 1.0


def test_ece_weights_bins_by_count() -> None:
    probs = [0.1] * 9 + [0.9]
    labels = [False] * 9 + [False]
    assert ece(probs, labels, n_bins=10) == pytest.approx((9 * 0.1 + 1 * 0.9) / 10)
