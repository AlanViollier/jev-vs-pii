"""How far a lane's confidence can be trusted: ECE, Brier, reliability bins."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel


class ReliabilityBin(BaseModel):
    """One confidence bucket: mean confidence vs how often it was right."""

    low: float
    high: float
    count: int
    mean_confidence: float
    accuracy: float


def ece(probs: Sequence[float], labels: Sequence[bool], n_bins: int = 10) -> float:
    """Expected calibration error over equal-width bins.

    Parameters
    ----------
    probs:
        Predicted probability of PII, one per word.
    labels:
        Gold truth per word.
    n_bins:
        Number of equal-width confidence bins.

    Returns
    -------
    float
        Count-weighted mean |confidence − accuracy|; 0 is perfectly calibrated.
    """
    raise NotImplementedError


def brier(probs: Sequence[float], labels: Sequence[bool]) -> float:
    """Mean squared error between probability and outcome (tested against scikit-learn)."""
    raise NotImplementedError


def reliability_bins(
    probs: Sequence[float], labels: Sequence[bool], n_bins: int = 10
) -> list[ReliabilityBin]:
    """Bins for the reliability diagram; empty bins are omitted."""
    raise NotImplementedError
