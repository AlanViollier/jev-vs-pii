"""Format-driven patterns only: emails, phones, IPs, card and ID numbers, dates, times.

Written from general knowledge of these formats, never tuned on either dataset.
"""

from __future__ import annotations

import re

from pii_bench.schema import Doc, LaneInfo, Prediction, Span
from pii_bench.taxonomy import Coarse

_MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?"
    r"|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?"
)
_DAY = r"\d{1,2}(?:st|nd|rd|th)?"

## Earlier patterns win when two matches start at the same place and are equally long.
_PATTERNS: list[tuple[Coarse, re.Pattern[str]]] = [
    ("CONTACT", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    (
        "CONTACT",
        re.compile(r"\b(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b"),
    ),
    ## Three or more colons keeps clock times (12:30:45) out.
    ("CONTACT", re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{0,4}:){3,7}[0-9A-Fa-f]{1,4}(?![\w:])")),
    ("ID", re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")),
    ("DATETIME", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("DATETIME", re.compile(r"\b\d{1,2}[/.-]\d{1,2}[/.-](?:\d{4}|\d{2})\b")),
    ("DATETIME", re.compile(rf"\b{_DAY}\s+(?:of\s+)?{_MONTH},?\s+\d{{4}}\b", re.IGNORECASE)),
    ("DATETIME", re.compile(rf"\b{_MONTH}\s+{_DAY},?\s+\d{{4}}\b", re.IGNORECASE)),
    ("DATETIME", re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?m\.?)?(?!\w)", re.IGNORECASE)),
    (
        "CONTACT",
        re.compile(
            r"(?<![\w+])(?:\+\d{1,3}[ .-]?)?(?:\(\d{1,4}\)[ .-]?)?\d{2,4}(?:[ .-]\d{2,4}){2,4}\b"
        ),
    ),
    ## An unbroken code of 6+ characters holding at least 4 digits: IDs, account and case numbers.
    ("ID", re.compile(r"\b(?=(?:[A-Za-z/-]*\d){4})[A-Za-z0-9][A-Za-z0-9/-]{4,}[A-Za-z0-9]\b")),
]


class RegexLane:
    """Lane `regex`: every pattern over the text, overlaps resolved leftmost-longest."""

    info = LaneInfo(id="regex", family="rules")

    async def predict(self, doc: Doc) -> Prediction:
        """Find format-driven PII in `doc`."""
        return Prediction(doc_id=doc.id, lane_id=self.info.id, spans=tuple(find_patterns(doc.text)))


def find_patterns(text: str) -> list[Span]:
    """Match every pattern and keep a non-overlapping set, leftmost first, longest on ties.

    Parameters
    ----------
    text:
        Source text.

    Returns
    -------
    list[Span]
        Labelled spans in text order.
    """
    matches = [
        (match.start(), -match.end(), priority, label)
        for priority, (label, pattern) in enumerate(_PATTERNS)
        for match in pattern.finditer(text)
    ]
    spans: list[Span] = []
    for start, negative_end, _, label in sorted(matches):
        if spans and start < spans[-1].end:
            continue
        spans.append(Span(start=start, end=-negative_end, label=label))
    return spans
