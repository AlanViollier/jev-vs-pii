"""One coarse label set shared by every dataset and lane."""

from __future__ import annotations

from typing import Literal

from pii_bench.schema import Dataset, Doc

Coarse = Literal["PERSON", "LOCATION", "CONTACT", "ID", "DATETIME", "OTHER"]
Shape = Literal["format", "context"]

## The type vocabulary every lane answers in, word for word.
DEFINITIONS: dict[Coarse, str] = {
    "PERSON": "A person's name or part of it, or a title used with it (Mr, Dr).",
    "LOCATION": "A place tied to a person: street, building or unit number, city, region, postcode, country, coordinates.",
    "CONTACT": "A way to reach or trace a person: email address, phone number, username or online handle, IP address.",
    "ID": "An identifying number or secret: ID card, social security, passport, driving licence, case or account number, password.",
    "DATETIME": "A date or time tied to a person, including birth dates and times of day.",
    "OTHER": "Any other detail that helps identify a person: sex or gender, nationality, organisation, job, age or amount.",
}

## Every dataset label -> (coarse type, shape). Shape: "format" when the surface gives it
## away (digits, @, a code pattern), "context" when only meaning does (a name, a place, a job).
_AI4PRIVACY: dict[str, tuple[Coarse, Shape]] = {
    "GIVENNAME1": ("PERSON", "context"),
    "GIVENNAME2": ("PERSON", "context"),
    "LASTNAME1": ("PERSON", "context"),
    "LASTNAME2": ("PERSON", "context"),
    "LASTNAME3": ("PERSON", "context"),
    "TITLE": ("PERSON", "context"),
    "STREET": ("LOCATION", "context"),
    "BUILDING": ("LOCATION", "format"),
    "SECADDRESS": ("LOCATION", "format"),
    "CITY": ("LOCATION", "context"),
    "STATE": ("LOCATION", "context"),
    "POSTCODE": ("LOCATION", "format"),
    "COUNTRY": ("LOCATION", "context"),
    "GEOCOORD": ("LOCATION", "format"),
    "EMAIL": ("CONTACT", "format"),
    "TEL": ("CONTACT", "format"),
    "USERNAME": ("CONTACT", "format"),
    "IP": ("CONTACT", "format"),
    "IDCARD": ("ID", "format"),
    "SOCIALNUMBER": ("ID", "format"),
    "PASSPORT": ("ID", "format"),
    "DRIVERLICENSE": ("ID", "format"),
    "PASS": ("ID", "format"),
    "DATE": ("DATETIME", "format"),
    "TIME": ("DATETIME", "format"),
    "BOD": ("DATETIME", "format"),
    "SEX": ("OTHER", "context"),
    "CARDISSUER": ("OTHER", "context"),
}

_TAB: dict[str, tuple[Coarse, Shape]] = {
    "PERSON": ("PERSON", "context"),
    "LOC": ("LOCATION", "context"),
    "ORG": ("OTHER", "context"),
    "DEM": ("OTHER", "context"),
    "MISC": ("OTHER", "context"),
    "CODE": ("ID", "format"),
    "DATETIME": ("DATETIME", "format"),
    "QUANTITY": ("OTHER", "format"),
}

_NEMOTRON: dict[str, tuple[Coarse, Shape]] = {
    "first_name": ("PERSON", "context"),
    "last_name": ("PERSON", "context"),
    "street_address": ("LOCATION", "context"),
    "city": ("LOCATION", "context"),
    "county": ("LOCATION", "context"),
    "state": ("LOCATION", "context"),
    "country": ("LOCATION", "context"),
    "postcode": ("LOCATION", "format"),
    "coordinate": ("LOCATION", "format"),
    "email": ("CONTACT", "format"),
    "phone_number": ("CONTACT", "format"),
    "fax_number": ("CONTACT", "format"),
    "url": ("CONTACT", "format"),
    "user_name": ("CONTACT", "format"),
    "ipv4": ("CONTACT", "format"),
    "ipv6": ("CONTACT", "format"),
    "mac_address": ("CONTACT", "format"),
    "http_cookie": ("CONTACT", "format"),
    **{
        label: ("ID", "format")
        for label in (
            "ssn",
            "national_id",
            "tax_id",
            "customer_id",
            "employee_id",
            "account_number",
            "credit_debit_card",
            "cvv",
            "pin",
            "bank_routing_number",
            "swift_bic",
            "medical_record_number",
            "health_plan_beneficiary_number",
            "certificate_license_number",
            "vehicle_identifier",
            "license_plate",
            "device_identifier",
            "unique_id",
            "api_key",
            "password",
            "biometric_identifier",
        )
    },
    "date": ("DATETIME", "format"),
    "time": ("DATETIME", "format"),
    "date_time": ("DATETIME", "format"),
    "date_of_birth": ("DATETIME", "format"),
    **{
        label: ("OTHER", "context")
        for label in (
            "company_name",
            "occupation",
            "employment_status",
            "education_level",
            "language",
            "gender",
            "age",
            "race_ethnicity",
            "religious_belief",
            "political_view",
            "sexuality",
            "blood_type",
        )
    },
}

_BY_DATASET: dict[Dataset, dict[str, tuple[Coarse, Shape]]] = {
    "ai4privacy": _AI4PRIVACY,
    "tab": _TAB,
    "nemotron": _NEMOTRON,
}

## What each dataset's annotators were told to mark, in plain words: from ai4privacy's and
## Nemotron-PII's label lists and TAB's published annotation guidelines, never from their text.
_AI4PRIVACY_GUIDE = (
    "Mark every piece of personal information about a person, of these kinds: given names "
    "and surnames, and titles used with them (Mr, Mrs, Dr); email addresses, phone numbers, "
    "usernames and IP addresses; ID card, social security, passport and driving licence "
    "numbers, and passwords; dates, dates of birth and times, including a bare hour; street "
    "names, building numbers, secondary address parts (apartment, suite), cities, states, "
    "postcodes, countries and coordinates; a person's sex or gender."
)
_NEMOTRON_GUIDE = (
    "Mark every piece of personal or sensitive information in this document, of these kinds: "
    "first and last names; dates, times and dates of birth; email addresses, phone and fax "
    "numbers, URLs, usernames, IP and MAC addresses, cookies; street addresses, cities, "
    "counties, states, countries, postcodes and coordinates; company names; ID and account "
    "numbers of every kind (social security, national and tax IDs, customer and employee IDs, "
    "medical record and health plan numbers, licence plates, vehicle and device identifiers, "
    "card numbers, CVV, PIN, bank routing and SWIFT codes, API keys, passwords, certificate "
    "numbers, biometric identifiers); occupation, employment status, education level, "
    "language, gender, age, race or ethnicity, religion, political view, sexuality and blood type."
)


def to_coarse(dataset: Dataset, label: str) -> Coarse:
    """Map a dataset's own label onto the coarse set.

    Parameters
    ----------
    dataset:
        Which dataset the label comes from.
    label:
        The dataset's label, e.g. `GIVENNAME1`, `LOC` or `phone_number`.

    Returns
    -------
    Coarse
        The coarse label; anything unmapped is `OTHER`.
    """
    return _BY_DATASET[dataset].get(label, ("OTHER", "context"))[0]


def shape(dataset: Dataset, label: str) -> Shape:
    """Whether a dataset label is found by its form or only by its meaning.

    Parameters
    ----------
    dataset:
        Which dataset the label comes from.
    label:
        The dataset's label; for TAB a gold `detail` like `QUASI DATETIME` works too.

    Returns
    -------
    Shape
        `format` for emails, numbers, codes, dates; `context` for names, places,
        organisations and personal attributes. Unmapped labels are `context`.
    """
    return _BY_DATASET[dataset].get(label.split()[-1], ("OTHER", "context"))[1]


def guidelines(doc: Doc) -> str:
    """What counts as PII in this doc, as the dataset's annotators were told.

    Parameters
    ----------
    doc:
        The doc a lane is about to label.

    Returns
    -------
    str
        The dataset's guideline paragraph; TAB's names the person to protect.
    """
    if doc.dataset == "ai4privacy":
        return _AI4PRIVACY_GUIDE
    if doc.dataset == "nemotron":
        return _NEMOTRON_GUIDE
    return (
        f"This is a European Court of Human Rights judgment. Mark what must be masked so that "
        f"{doc.subject} cannot be re-identified, and nothing more: keep as much text as possible.\n"
        f"Mask direct identifiers: anything that on its own points to {doc.subject}, such as "
        "their name (with titles like Mr or Mrs) or a number or code that belongs to them.\n"
        f"Mask quasi-identifiers: details that could re-identify {doc.subject} when combined "
        "with each other and with public knowledge (news, social media, public records; not the "
        "judgment itself). These usually include dates of events in their story (birth, arrest, "
        "hearings, decisions), places they lived or went, organisations tied to them (employers, "
        "prisons, hospitals, schools, local offices), names of relatives and other people "
        "involved, their personal attributes (age, nationality, ethnicity, job, education, "
        "health), case numbers, and meaningful amounts.\n"
        "Leave: details so general they fit many people (such as a country of birth on its own), "
        "pronouns, the job titles of legal professionals (lawyer, solicitor), and parts of "
        "generic legal references (such as the year a law was passed)."
    )


def definition(doc: Doc) -> str:
    """The full brief a lane gives its model: the dataset's guidelines, then the type vocabulary.

    Parameters
    ----------
    doc:
        The doc a lane is about to label.

    Returns
    -------
    str
        `guidelines(doc)`, then one `TYPE: meaning` line per coarse type for typed answers.
    """
    types = "\n".join(f"{label}: {meaning}" for label, meaning in DEFINITIONS.items())
    return f"{guidelines(doc)}\n\nTypes to use:\n{types}"
