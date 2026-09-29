"""Every dataset label lands on exactly one coarse type."""

from __future__ import annotations

import pytest

from jev_vs_pii.schema import Dataset, Doc
from jev_vs_pii.taxonomy import DEFINITIONS, definition, guidelines, shape, to_coarse


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


def test_tab_guidelines_name_the_person_to_protect() -> None:
    doc = Doc(id="d", dataset="tab", split="test", text="x", gold=(), subject="Ivo Brandt")
    assert "Ivo Brandt" in guidelines(doc)


def test_ai4privacy_guidelines_have_no_subject() -> None:
    doc = Doc(id="d", dataset="ai4privacy", split="test", text="x", gold=())
    assert "None" not in guidelines(doc)


def test_every_coarse_type_is_defined() -> None:
    assert set(DEFINITIONS) == {"PERSON", "LOCATION", "CONTACT", "ID", "DATETIME", "OTHER"}


def test_definition_is_guidelines_then_every_type() -> None:
    doc = Doc(id="d", dataset="tab", split="test", text="x", gold=(), subject="Ivo Brandt")
    text = definition(doc)
    assert text.startswith(guidelines(doc))
    assert all(f"{label}: {meaning}" in text for label, meaning in DEFINITIONS.items())


@pytest.mark.parametrize(
    ("dataset", "label", "coarse", "found_by"),
    [
        ("nemotron", "first_name", "PERSON", "context"),
        ("nemotron", "swift_bic", "ID", "format"),
        ("nemotron", "http_cookie", "CONTACT", "format"),
        ("nemotron", "religious_belief", "OTHER", "context"),
        ("ai4privacy", "BUILDING", "LOCATION", "format"),
        ("ai4privacy", "SEX", "OTHER", "context"),
        ("tab", "QUANTITY", "OTHER", "format"),
        ("tab", "DEM", "OTHER", "context"),
    ],
)
def test_labels_map_to_a_type_and_a_shape(
    dataset: Dataset, label: str, coarse: str, found_by: str
) -> None:
    assert (to_coarse(dataset, label), shape(dataset, label)) == (coarse, found_by)


def test_nemotron_guidelines_name_every_kind_of_label() -> None:
    doc = Doc(id="n", dataset="nemotron", split="test", text="x", gold=())
    text = guidelines(doc).lower()
    for kind in ("swift", "cookie", "blood type", "religion", "company names", "biometric"):
        assert kind in text
