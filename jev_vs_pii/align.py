"""Map an LLM's text answer back onto character offsets in the source."""

from __future__ import annotations

import bisect
import re
from collections.abc import Sequence
from difflib import SequenceMatcher

from pydantic import BaseModel

from jev_vs_pii.exceptions import AlignmentError
from jev_vs_pii.schema import Span
from jev_vs_pii.taxonomy import DEFINITIONS

## Share of the source a tagged rewrite must reproduce before its tags are trusted.
_MIN_REPRODUCED = 0.9
_TAG = re.compile(rf"<(/?)({'|'.join(DEFINITIONS)})>")


class Mention(BaseModel):
    """A PII string an LLM said back, with its type."""

    text: str
    label: str


def find_mentions(source: str, mentions: Sequence[Mention]) -> tuple[list[Span], int]:
    """Locate every occurrence of every mention in `source`.

    Parameters
    ----------
    source:
        Original doc text.
    mentions:
        Strings the LLM reported. Matching ignores case, any run of whitespace between
        words, and punctuation beside it; a mention never matches inside a longer word.

    Returns
    -------
    tuple[list[Span], int]
        One span per distinct occurrence found, in text order, and how many mentions
        were found nowhere (the lane's alignment failures).
    """
    spans: set[Span] = set()
    missing = 0
    for mention in mentions:
        found = [
            Span(start=match.start(), end=match.end(), label=mention.label)
            for match in _mention_pattern(mention.text).finditer(source)
        ]
        missing += not found
        spans.update(found)
    return sorted(spans, key=lambda span: (span.start, span.end)), missing


def parse_tagged(source: str, tagged: str) -> tuple[list[Span], int]:
    """Recover spans from a tagged rewrite like `Call <PERSON>Marie</PERSON> at ...`.

    Parameters
    ----------
    source:
        Original doc text.
    tagged:
        The LLM's rewrite of `source` with PII wrapped in `<LABEL>...</LABEL>` tags.
        Unmatched tags are ignored.

    Returns
    -------
    tuple[list[Span], int]
        Spans in `source` offsets, and how many tagged items fell entirely in text the
        rewrite changed. Raises `AlignmentError` when the untagged rewrite reproduces
        less than 90% of `source`.
    """
    plain, tagged_spans = _strip_tags(tagged)
    if plain == source:
        return tagged_spans, 0
    blocks = [
        block
        for block in SequenceMatcher(None, source, plain, autojunk=False).get_matching_blocks()
        if block.size
    ]
    reproduced = sum(block.size for block in blocks) / max(len(source), 1)
    if reproduced < _MIN_REPRODUCED:
        raise AlignmentError(f"rewrite reproduces only {reproduced:.0%} of the source")
    spans = []
    for span in tagged_spans:
        start, end = _to_source(blocks, span.start, span.end)
        if start < end:
            spans.append(Span(start=start, end=end, label=span.label))
    return spans, len(tagged_spans) - len(spans)


def _mention_pattern(text: str) -> re.Pattern[str]:
    """Case-blind pattern that can't start or end mid-word; between words any spacing, and
    punctuation next to it, is allowed (`Mr Daniel` finds `Mr. Daniel`), and straight and
    curly quotes match each other (`O'Neill` finds `O’Neill`)."""
    body = r"[^\w\s]*\s+[^\w\s]*".join(_escape(token) for token in text.split())
    left = r"(?<!\w)" if re.match(r"\w", text.strip()) else ""
    right = r"(?!\w)" if re.search(r"\w$", text.strip()) else ""
    return re.compile(f"{left}{body}{right}", re.IGNORECASE)


## Each group matches any of its members: LLMs write straight quotes, legal text curly ones.
_QUOTE_GROUPS = ("'’‘ʼ", '"“”')


def _escape(token: str) -> str:
    escaped = re.escape(token)
    for group in _QUOTE_GROUPS:
        escaped = re.sub(f"[{group}]", f"[{group}]", escaped)
    return escaped


def _strip_tags(tagged: str) -> tuple[str, list[Span]]:
    """Remove tags, returning the plain text and the tagged spans in its offsets."""
    plain: list[str] = []
    length = 0
    open_label: str | None = None
    open_at = 0
    spans = []
    cursor = 0
    for match in _TAG.finditer(tagged):
        piece = tagged[cursor : match.start()]
        plain.append(piece)
        length += len(piece)
        cursor = match.end()
        closing, label = match.group(1) == "/", match.group(2)
        if not closing:
            open_label, open_at = label, length
        elif label == open_label:
            if length > open_at:
                spans.append(Span(start=open_at, end=length, label=label))
            open_label = None
    plain.append(tagged[cursor:])
    return "".join(plain), spans


def _to_source(blocks: Sequence[tuple[int, int, int]], start: int, end: int) -> tuple[int, int]:
    """Map a half-open range in the rewrite to the source, shrinking it to reproduced text."""
    starts = [b for _, b, _ in blocks]
    ## First block that ends after `start`, then the last block that starts before `end`.
    first = bisect.bisect_right([b + size for _, b, size in blocks], start)
    last = bisect.bisect_left(starts, end) - 1
    if first >= len(blocks) or last < 0 or first > last:
        return 0, 0
    a, b, _ = blocks[first]
    source_start = a + max(start - b, 0)
    a, b, size = blocks[last]
    source_end = a + min(end - b, size)
    return source_start, source_end
