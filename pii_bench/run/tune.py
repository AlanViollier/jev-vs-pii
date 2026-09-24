"""Pick decoder knobs on the dev split. Never on test."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.decode import DecodeParams
from pii_bench.schema import Doc, MatchMode, Prediction


def tune_decoder(
    docs: Sequence[Doc],
    predictions: Sequence[Prediction],
    grid: Sequence[DecodeParams],
    mode: MatchMode,
) -> tuple[DecodeParams, float]:
    """Grid-search decoder settings on cached word scores, maximising F2.

    Parameters
    ----------
    docs:
        Dev-split docs.
    predictions:
        A per-word lane's dev predictions (must carry `word_scores`).
    grid:
        Candidate settings, any mix of decoders.
    mode:
        Match mode the F2 is computed under.

    Returns
    -------
    tuple[DecodeParams, float]
        Best settings and their dev F2.
    """
    raise NotImplementedError
