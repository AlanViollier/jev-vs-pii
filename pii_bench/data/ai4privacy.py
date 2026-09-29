"""Load ai4privacy English docs. Dev is sampled from its train file, test from its validation file."""

from __future__ import annotations

import random
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from pii_bench.data.fetch import AI4PRIVACY_FILES
from pii_bench.schema import Doc, Span, Split
from pii_bench.taxonomy import to_coarse


class _Mask(BaseModel):
    value: str
    start: int
    end: int
    label: str


class _Row(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    source_text: str
    privacy_mask: list[_Mask]


def load_ai4privacy(data_dir: Path, split: Split, n: int, seed: int) -> list[Doc]:
    """Load a seeded sample of `n` English docs with gold spans mapped to coarse labels.

    Docs whose gold values don't match the text at their offsets are dropped before
    sampling: 23 of 7,946 in the validation file carry leftover markup in their spans.

    Parameters
    ----------
    data_dir:
        Root data directory holding the fetched files.
    split:
        `dev` samples the train file, `test` the validation file.
    n:
        Sample size (500 for each split).
    seed:
        Sampling seed; same seed, same docs.

    Returns
    -------
    list[Doc]
        Docs in a stable order.
    """
    path = data_dir / "ai4privacy" / AI4PRIVACY_FILES[split]
    with path.open(encoding="utf-8") as lines:
        rows = [_Row.model_validate_json(line) for line in lines]
    aligned = [row for row in rows if _is_aligned(row)]
    sample = random.Random(seed).sample(aligned, n)  # nosec B311: reproducible sampling, not security
    return [_to_doc(row, split) for row in sample]


def _is_aligned(row: _Row) -> bool:
    """Every gold value sits exactly at its offsets."""
    return all(row.source_text[m.start : m.end] == m.value for m in row.privacy_mask)


def _to_doc(row: _Row, split: Split) -> Doc:
    gold = sorted(
        (
            Span(start=m.start, end=m.end, label=to_coarse("ai4privacy", m.label))
            for m in row.privacy_mask
        ),
        key=lambda span: (span.start, span.end),
    )
    return Doc(id=row.id, dataset="ai4privacy", split=split, text=row.source_text, gold=tuple(gold))
