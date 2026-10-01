"""One door to every benchmark split, with the sample sizes the results are reported on."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from jev_vs_pii.data.ai4privacy import load_ai4privacy
from jev_vs_pii.data.nemotron import load_nemotron
from jev_vs_pii.data.tab import load_tab
from jev_vs_pii.exceptions import DataError
from jev_vs_pii.schema import Dataset, Doc, Split

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
        Same docs, same order, on every call with the same arguments. Raises `DataError`
        if two docs share an id.
    """
    if dataset == "ai4privacy":
        docs = load_ai4privacy(data_dir, split, SAMPLE_SIZE, seed)
    elif dataset == "nemotron":
        docs = load_nemotron(data_dir, split, SAMPLE_SIZE, seed)
    else:
        docs = load_tab(data_dir, split)
    ## Scoring finds gold by doc id: a shared id would score one doc against another's gold.
    repeated = sorted(doc_id for doc_id, n in Counter(doc.id for doc in docs).items() if n > 1)
    if repeated:
        raise DataError(f"{dataset} {split}: doc ids not unique: {', '.join(repeated[:5])}")
    return docs
