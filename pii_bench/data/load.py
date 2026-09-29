"""One door to every benchmark split, with the sample sizes the results are reported on."""

from __future__ import annotations

from pathlib import Path

from pii_bench.data.ai4privacy import load_ai4privacy
from pii_bench.data.nemotron import load_nemotron
from pii_bench.data.tab import load_tab
from pii_bench.schema import Dataset, Doc, Split

## ai4privacy and Nemotron-PII are sampled (500 keeps a F2 CI near ±0.02); TAB is used whole.
SAMPLE_SIZE = 500


def load_docs(data_dir: Path, dataset: Dataset, split: Split, seed: int) -> list[Doc]:
    """Load a benchmark split in its stable order.

    Parameters
    ----------
    data_dir:
        Root data directory holding the fetched files.
    dataset:
        `ai4privacy`, `tab` or `nemotron`.
    split:
        `dev` (tuning only) or `test` (reported numbers).
    seed:
        Sampling seed for the sampled datasets.

    Returns
    -------
    list[Doc]
        Same docs, same order, on every call with the same arguments.
    """
    if dataset == "ai4privacy":
        return load_ai4privacy(data_dir, split, SAMPLE_SIZE, seed)
    if dataset == "nemotron":
        return load_nemotron(data_dir, split, SAMPLE_SIZE, seed)
    return load_tab(data_dir, split)
