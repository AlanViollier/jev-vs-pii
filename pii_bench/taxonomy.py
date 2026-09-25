"""One coarse label set shared by every dataset and lane."""

from __future__ import annotations

from typing import Literal

from pii_bench.schema import Dataset, Doc

Coarse = Literal["PERSON", "LOCATION", "CONTACT", "ID", "DATETIME", "OTHER"]

## The one definition every lane is given, word for word. Written from the datasets'
## label schemes, never from their text, so it tunes nothing on gold.
DEFINITIONS: dict[Coarse, str] = {
    "PERSON": "A person's name or part of it, or a title used with it (Mr, Dr).",
    "LOCATION": "A place tied to a person: street, building or unit number, city, region, postcode, country, coordinates.",
    "CONTACT": "A way to reach or trace a person: email address, phone number, username or online handle, IP address.",
    "ID": "An identifying number or secret: ID card, social security, passport, driving licence, case or account number, password.",
    "DATETIME": "A date or time tied to a person, including birth dates and times of day.",
    "OTHER": "Any other detail that helps identify a person: sex or gender, nationality, organisation, job, age or amount.",
}

_AI4PRIVACY_SCOPE = "Mark every piece of personal information of the kinds below."

_AI4PRIVACY: dict[str, Coarse] = {
    "GIVENNAME1": "PERSON",
    "GIVENNAME2": "PERSON",
    "LASTNAME1": "PERSON",
    "LASTNAME2": "PERSON",
    "LASTNAME3": "PERSON",
    "TITLE": "PERSON",
    "STREET": "LOCATION",
    "BUILDING": "LOCATION",
    "SECADDRESS": "LOCATION",
    "CITY": "LOCATION",
    "STATE": "LOCATION",
    "POSTCODE": "LOCATION",
    "COUNTRY": "LOCATION",
    "GEOCOORD": "LOCATION",
    "EMAIL": "CONTACT",
    "TEL": "CONTACT",
    "USERNAME": "CONTACT",
    "IP": "CONTACT",
    "IDCARD": "ID",
    "SOCIALNUMBER": "ID",
    "PASSPORT": "ID",
    "DRIVERLICENSE": "ID",
    "PASS": "ID",
    "DATE": "DATETIME",
    "TIME": "DATETIME",
    "BOD": "DATETIME",
}

_TAB: dict[str, Coarse] = {
    "PERSON": "PERSON",
    "LOC": "LOCATION",
    "CODE": "ID",
    "DATETIME": "DATETIME",
}

_BY_DATASET: dict[Dataset, dict[str, Coarse]] = {"ai4privacy": _AI4PRIVACY, "tab": _TAB}


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
        The coarse label; anything unmapped (SEX, CARDISSUER, TAB's ORG, DEM, MISC,
        QUANTITY) is `OTHER`.
    """
    return _BY_DATASET[dataset].get(label, "OTHER")


def scope(doc: Doc) -> str:
    """Say what counts as PII in this doc; every lane puts it before `DEFINITIONS`.

    ai4privacy wants every kind of personal information; TAB only what re-identifies
    the one person its annotators were asked to protect.

    Parameters
    ----------
    doc:
        The doc a lane is about to label.

    Returns
    -------
    str
        One instruction paragraph.
    """
    if doc.dataset == "ai4privacy":
        return _AI4PRIVACY_SCOPE
    return (
        f"This is a court judgment. Mark only what must be masked so that {doc.subject} "
        "cannot be identified, directly or combined with other details and public knowledge. "
        "Leave everything that does not point to them, such as the court, laws, public bodies "
        "or the state being sued."
    )
