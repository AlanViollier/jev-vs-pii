"""Loaders on hand-written fixtures in each dataset's format; fetch never re-downloads."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pyarrow as pa  # type: ignore[import-untyped]  # ships no type hints
import pyarrow.parquet as pq  # type: ignore[import-untyped]
import pytest

from jev_vs_pii.data import fetch as fetch_module
from jev_vs_pii.data import load_ai4privacy, load_nemotron, load_tab
from jev_vs_pii.data.fetch import AI4PRIVACY_FILES, NEMOTRON_FILES, TAB_FILES, fetch_tab
from jev_vs_pii.schema import Split


def _ai4privacy_row(doc_id: str, text: str, masks: list[tuple[str, str]]) -> dict[str, object]:
    privacy_mask = []
    for value, label in masks:
        start = text.index(value)
        privacy_mask.append(
            {"value": value, "start": start, "end": start + len(value), "label": label}
        )
    return {"id": doc_id, "source_text": text, "privacy_mask": privacy_mask, "language": "English"}


def _write_ai4privacy(data_dir: Path, split: Split, rows: list[dict[str, object]]) -> None:
    path = data_dir / "ai4privacy" / AI4PRIVACY_FILES[split]
    path.parent.mkdir(parents=True)
    path.write_text("".join(f"{json.dumps(row)}\n" for row in rows))


def _mention(text: str, value: str, entity_type: str, identifier_type: str) -> dict[str, object]:
    start = text.index(value)
    return {
        "start_offset": start,
        "end_offset": start + len(value),
        "span_text": value,
        "entity_type": entity_type,
        "identifier_type": identifier_type,
    }


@pytest.fixture
def ai4privacy_dir(tmp_path: Path) -> Path:
    rows = [
        _ai4privacy_row(
            f"doc{i}",
            f"Ticket {i} for Nora Quill, born 3 May 1990, reach her at nq{i}@mail.test.",
            [
                ("Nora", "GIVENNAME1"),
                ("Quill", "LASTNAME1"),
                ("3 May 1990", "BOD"),
                (f"nq{i}@mail.test", "EMAIL"),
            ],
        )
        for i in range(6)
    ]
    broken = _ai4privacy_row("broken", "Call TEL_BG(555 0100 now.", [("555 0100", "TEL")])
    broken["privacy_mask"][0]["value"] = "TEL_BG(555 0100"  # type: ignore[index]  # fixture mimics real markup leaks
    _write_ai4privacy(tmp_path, "test", [*rows, broken])
    _write_ai4privacy(tmp_path, "dev", rows[:3])
    return tmp_path


def test_ai4privacy_gold_is_coarse_and_points_into_text(ai4privacy_dir: Path) -> None:
    (doc,) = load_ai4privacy(ai4privacy_dir, "test", n=1, seed=0)
    assert [doc.text[s.start : s.end] for s in doc.gold][:2] == ["Nora", "Quill"]
    assert [s.label for s in doc.gold] == ["PERSON", "PERSON", "DATETIME", "CONTACT"]
    assert doc.dataset == "ai4privacy"
    assert doc.split == "test"


def test_ai4privacy_drops_docs_with_misaligned_gold(ai4privacy_dir: Path) -> None:
    docs = load_ai4privacy(ai4privacy_dir, "test", n=6, seed=0)
    assert "broken" not in {doc.id for doc in docs}
    with pytest.raises(ValueError):
        load_ai4privacy(ai4privacy_dir, "test", n=7, seed=0)


def test_ai4privacy_same_seed_same_sample(ai4privacy_dir: Path) -> None:
    first = [d.id for d in load_ai4privacy(ai4privacy_dir, "test", n=3, seed=7)]
    again = [d.id for d in load_ai4privacy(ai4privacy_dir, "test", n=3, seed=7)]
    other = [d.id for d in load_ai4privacy(ai4privacy_dir, "test", n=3, seed=8)]
    assert first == again
    assert first != other


def test_ai4privacy_dev_reads_the_train_file(ai4privacy_dir: Path) -> None:
    docs = load_ai4privacy(ai4privacy_dir, "dev", n=3, seed=0)
    assert {d.id for d in docs} == {"doc0", "doc1", "doc2"}
    assert {d.split for d in docs} == {"dev"}


def test_tab_gold_is_masked_mentions_of_first_annotator(tmp_path: Path) -> None:
    text = "The applicant, Ivo Brandt, was born in 1961 in Tromsø. The Court of Appeal dismissed the case."
    first = [
        _mention(text, "Ivo Brandt", "PERSON", "DIRECT"),
        _mention(text, "1961", "DATETIME", "QUASI"),
        _mention(text, "Tromsø", "LOC", "QUASI"),
        _mention(text, "Court of Appeal", "ORG", "NO_MASK"),
    ]
    second = [_mention(text, "Ivo Brandt", "PERSON", "DIRECT")]
    doc_json = {
        "doc_id": "001-1",
        "text": text,
        "task": "Task: Annotate the document to anonymise the following person: Ivo Brandt",
        "meta": {"applicant": "Ivo Brandt", "year": 2004},
        "annotations": {
            "annotator1": {"entity_mentions": first},
            "annotator2": {"entity_mentions": second},
        },
    }
    (tmp_path / "tab").mkdir()
    (tmp_path / "tab" / TAB_FILES["test"]).write_text(json.dumps([doc_json]))

    (doc,) = load_tab(tmp_path, "test")
    assert [doc.text[s.start : s.end] for s in doc.gold] == ["Ivo Brandt", "1961", "Tromsø"]
    assert [s.label for s in doc.gold] == ["PERSON", "DATETIME", "LOCATION"]
    assert doc.subject == "Ivo Brandt"
    assert [[doc.text[s.start : s.end] for s in spans] for spans in doc.other_annotators] == [
        ["Ivo Brandt"]
    ]
    assert [doc.text[s.start : s.end] for s in doc.cleared] == ["Court of Appeal"]
    assert [s.detail for s in doc.gold] == ["DIRECT PERSON", "QUASI DATETIME", "QUASI LOC"]


def _nemotron_row(uid: str, text: str, fmt: str, spans: list[tuple[str, str]]) -> dict[str, str]:
    mentions = [
        {
            "start": text.index(value),
            "end": text.index(value) + len(value),
            "text": value,
            "label": label,
        }
        for value, label in spans
    ]
    return {"uid": uid, "text": text, "spans": str(mentions), "document_format": fmt}


def test_nemotron_keeps_aligned_unstructured_docs_with_fine_labels(tmp_path: Path) -> None:
    text = "Dear Lena Ortiz, your account 88-1203 was reviewed on 2024-02-11."
    good = [("Lena", "first_name"), ("Ortiz", "last_name"), ("88-1203", "account_number")]
    rows = [
        *(_nemotron_row(f"u{i}", text, "unstructured", good) for i in range(3)),
        _nemotron_row("form", text, "structured", good),
        _nemotron_row("shifted", text, "unstructured", [("Lena", "first_name")]),
    ]
    rows[-1]["spans"] = str([{"start": 0, "end": 4, "text": "Lena", "label": "first_name"}])
    path = tmp_path / "nemotron" / NEMOTRON_FILES["test"]
    path.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(rows), path)

    docs = load_nemotron(tmp_path, "test", n=3, seed=0)
    assert sorted(d.id for d in docs) == ["u0", "u1", "u2"]
    assert [(docs[0].text[s.start : s.end], s.label, s.detail) for s in docs[0].gold] == [
        ("Lena", "PERSON", "first_name"),
        ("Ortiz", "PERSON", "last_name"),
        ("88-1203", "ID", "account_number"),
    ]
    with pytest.raises(ValueError):
        load_nemotron(tmp_path, "test", n=4, seed=0)


def test_fetch_tab_skips_files_already_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab_dir = tmp_path / "tab"
    tab_dir.mkdir()
    for name in (*TAB_FILES.values(), fetch_module.TAB_EVAL_SCRIPT):
        (tab_dir / name).write_text("present")

    def _no_network(*args: object, **kwargs: object) -> None:
        raise httpx.ConnectError("network used")

    monkeypatch.setattr(httpx, "stream", _no_network)
    assert fetch_tab(tmp_path) == tab_dir
