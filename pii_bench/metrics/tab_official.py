"""Score TAB predictions with TAB's own evaluation script, so the numbers match its paper."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel

from pii_bench.schema import Prediction


class TabScores(BaseModel):
    """TAB's headline metrics: entity recall on direct and quasi identifiers, weighted precision."""

    recall_direct: float
    recall_quasi: float
    precision_weighted: float


def run_tab_eval(predictions: Sequence[Prediction], tab_dir: Path, split: str) -> TabScores:
    """Write predictions in TAB's format and run its `evaluation.py` on them.

    Parameters
    ----------
    predictions:
        One lane's predictions on a TAB split.
    tab_dir:
        Fetched TAB directory, holding the split JSON and `evaluation.py`.
    split:
        `dev` or `test`.

    Returns
    -------
    TabScores
        Parsed from the script's output.
    """
    raise NotImplementedError
