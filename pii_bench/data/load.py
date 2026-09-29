"""One door to every benchmark split, with the sample sizes the results are reported on."""

from __future__ import annotations

from pathlib import Path

from pii_bench.data.ai4privacy import load_ai4privacy
from pii_bench.data.tab import load_tab
from pii_bench.schema import Dataset, Doc, Split

## ai4privacy is sampled; TAB is used whole (127 docs per split).
AI4PRIVACY_SIZES: dict[Split, int] = {"dev": 500, "test": 1000}


def load_docs(data_dir: Path, dataset: Dataset, split: Split, seed: int) -> list[Doc]:
    """Load a benchmark split in its stable order.

    Parameters
    ----------
    data_dir:
        Root data directory holding the fetched files.
    dataset:
        `ai4privacy` or `tab`.
    split:
        `dev` (tuning only) or `test` (reported numbers).
    seed:
        ai4privacy sampling seed.

    Returns
    -------
    list[Doc]
        Same docs, same order, on every call with the same arguments.
    """
    if dataset == "ai4privacy":
        return load_ai4privacy(data_dir, split, AI4PRIVACY_SIZES[split], seed)
    return load_tab(data_dir, split)
