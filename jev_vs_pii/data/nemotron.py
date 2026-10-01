"""Load Nemotron-PII's unstructured English documents: synthetic business prose, 55 PII labels."""

from __future__ import annotations

import ast
import random
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq  # type: ignore[import-untyped]  # ships no type hints
from pydantic import BaseModel, ConfigDict, TypeAdapter

from jev_vs_pii.data.fetch import NEMOTRON_FILES
from jev_vs_pii.schema import Doc, Span, Split
from jev_vs_pii.taxonomy import to_coarse

_COLUMNS = ["uid", "text", "spans", "document_format"]


class _Mention(BaseModel):
    ## A few values are stored as numbers (an age of 44).
    model_config = ConfigDict(coerce_numbers_to_str=True)

    start: int
    end: int
    text: str
    label: str


_MENTIONS = TypeAdapter(list[_Mention])


def load_nemotron(data_dir: Path, split: Split, n: int, seed: int) -> list[Doc]:
    """Load a seeded sample of `n` unstructured docs with gold spans mapped to coarse labels.

    Structured records (JSON-like forms) are left out: the set stands for everyday prose.
    Docs whose gold values don't match the text at their offsets are dropped before sampling.

    Parameters
    ----------
    data_dir:
        Root data directory holding the fetched files.
    split:
        `dev` samples the train file, `test` the test file.
    n:
        Sample size.
    seed:
        Sampling seed; same seed, same docs.

    Returns
    -------
    list[Doc]
        Docs in a stable order.
    """
    table = pq.read_table(
        data_dir / "nemotron" / NEMOTRON_FILES[split],
        columns=_COLUMNS,
        filters=[("document_format", "=", "unstructured")],
    )
    usable = []
    seen: Counter[str] = Counter()
    for row in table.to_pylist():
        ## The file reuses some uids for different docs: a repeat gets its file-order count.
        seen[row["uid"]] += 1
        uid = row["uid"] if seen[row["uid"]] == 1 else f"{row['uid']}-{seen[row['uid']]}"
        ## The spans column is a Python literal (single quotes), not JSON.
        mentions = _MENTIONS.validate_python(ast.literal_eval(row["spans"]))
        if all(row["text"][m.start : m.end] == m.text for m in mentions):
            usable.append((uid, row["text"], mentions))
    sample = random.Random(seed).sample(usable, n)  # nosec B311: reproducible sampling, not security
    return [_to_doc(uid, text, mentions, split) for uid, text, mentions in sample]


def _to_doc(uid: str, text: str, mentions: list[_Mention], split: Split) -> Doc:
    gold = {
        Span(start=m.start, end=m.end, label=to_coarse("nemotron", m.label), detail=m.label)
        for m in mentions
    }
    return Doc(
        id=uid,
        dataset="nemotron",
        split=split,
        text=text,
        gold=tuple(sorted(gold, key=lambda span: (span.start, span.end))),
    )
