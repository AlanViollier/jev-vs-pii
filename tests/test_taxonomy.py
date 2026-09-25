"""Every dataset label lands on exactly one coarse type."""

from __future__ import annotations

import pytest

from pii_bench.schema import Dataset, Doc
from pii_bench.taxonomy import DEFINITIONS, scope, to_coarse


@pytest.mark.parametrize(
    ("dataset", "label", "coarse"),
    [
        ("ai4privacy", "GIVENNAME2", "PERSON"),
        ("ai4privacy", "LASTNAME3", "PERSON"),
        ("ai4privacy", "SECADDRESS", "LOCATION"),
        ("ai4privacy", "USERNAME", "CONTACT"),
        ("ai4privacy", "PASS", "ID"),
        ("ai4privacy", "BOD", "DATETIME"),
        ("ai4privacy", "SEX", "OTHER"),
        ("tab", "LOC", "LOCATION"),
        ("tab", "CODE", "ID"),
        ("tab", "ORG", "OTHER"),
        ("tab", "QUANTITY", "OTHER"),
    ],
)
def test_label_maps_to_coarse(dataset: Dataset, label: str, coarse: str) -> None:
    assert to_coarse(dataset, label) == coarse


def test_unknown_label_is_other() -> None:
    assert to_coarse("ai4privacy", "NOT_A_LABEL") == "OTHER"


def test_tab_scope_names_the_person_to_protect() -> None:
    doc = Doc(id="d", dataset="tab", split="test", text="x", gold=(), subject="Ivo Brandt")
    assert "Ivo Brandt" in scope(doc)


def test_ai4privacy_scope_has_no_subject() -> None:
    doc = Doc(id="d", dataset="ai4privacy", split="test", text="x", gold=())
    assert "None" not in scope(doc)


def test_every_coarse_type_is_defined() -> None:
    assert set(DEFINITIONS) == {"PERSON", "LOCATION", "CONTACT", "ID", "DATETIME", "OTHER"}
