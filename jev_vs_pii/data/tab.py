"""Load TAB court judgments. Gold = mentions that must be masked (DIRECT + QUASI)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, TypeAdapter

from jev_vs_pii.data.fetch import TAB_FILES
from jev_vs_pii.schema import Doc, Span, Split
from jev_vs_pii.taxonomy import to_coarse


class _Mention(BaseModel):
    model_config = ConfigDict(extra="ignore")

    start_offset: int
    end_offset: int
    entity_type: str
    identifier_type: Literal["DIRECT", "QUASI", "NO_MASK"]


class _Annotation(BaseModel):
    entity_mentions: list[_Mention]


class _Meta(BaseModel):
    model_config = ConfigDict(extra="ignore")

    applicant: str


class _TabDoc(BaseModel):
    model_config = ConfigDict(extra="ignore")

    doc_id: str
    text: str
    meta: _Meta
    annotations: dict[str, _Annotation]


_TAB_DOCS = TypeAdapter(list[_TabDoc])


def load_tab(data_dir: Path, split: Split) -> list[Doc]:
    """Load one TAB split with every annotator's masking decisions.

    Parameters
    ----------
    data_dir:
        Root data directory holding the fetched files.
    split:
        `dev` or `test`, 127 docs each.

    Returns
    -------
    list[Doc]
        The first annotator's masking decisions are `gold` and, for what it left unmasked,
        `cleared`; the other annotators are not used. `subject` is the applicant, the person
        to protect.
    """
    raw = _TAB_DOCS.validate_json((data_dir / "tab" / TAB_FILES[split]).read_bytes())
    return [_to_doc(doc, split) for doc in raw]


def _to_doc(doc: _TabDoc, split: Split) -> Doc:
    first = next(iter(doc.annotations.values()))
    return Doc(
        id=doc.doc_id,
        dataset="tab",
        split=split,
        text=doc.text,
        gold=_spans(first, masked=True),
        subject=doc.meta.applicant,
        cleared=_spans(first, masked=False),
    )


def _spans(annotation: _Annotation, masked: bool) -> tuple[Span, ...]:
    """One annotator's mentions to mask (DIRECT, QUASI) or to leave (NO_MASK), in text order."""
    spans = {
        Span(
            start=m.start_offset,
            end=m.end_offset,
            label=to_coarse("tab", m.entity_type),
            detail=f"{m.identifier_type} {m.entity_type}",
        )
        for m in annotation.entity_mentions
        if (m.identifier_type != "NO_MASK") == masked
    }
    return tuple(sorted(spans, key=lambda span: (span.start, span.end)))
