"""One coarse label set shared by every dataset and lane."""

from __future__ import annotations

from typing import Literal

from pii_bench.schema import Dataset

Coarse = Literal["PERSON", "LOCATION", "CONTACT", "ID", "DATETIME", "OTHER"]


def to_coarse(dataset: Dataset, label: str) -> Coarse:
    """Map a dataset's own label onto the coarse set.

    Parameters
    ----------
    dataset:
        Which dataset the label comes from.
    label:
        The dataset's label, e.g. `GIVENNAME1` or `LOC`.

    Returns
    -------
    Coarse
        The coarse label; unknown labels map to `OTHER`.
    """
    raise NotImplementedError
