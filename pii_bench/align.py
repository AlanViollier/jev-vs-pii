"""Map an LLM's text answer back onto character offsets in the source."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel

from pii_bench.schema import Span


class Mention(BaseModel):
    """A PII string an LLM said back, with its type."""

    text: str
    label: str


def find_mentions(source: str, mentions: Sequence[Mention]) -> list[Span]:
    """Locate every occurrence of every mention in `source`.

    Parameters
    ----------
    source:
        Original doc text.
    mentions:
        Strings the LLM reported; matching tolerates whitespace and case differences.

    Returns
    -------
    list[Span]
        One span per occurrence found. Mentions not found anywhere are dropped and counted
        by the caller as the lane's alignment failures.
    """
    raise NotImplementedError


def parse_tagged(source: str, tagged: str) -> list[Span]:
    """Recover spans from a tagged rewrite like `Call <PERSON>Marie</PERSON> at ...`.

    Parameters
    ----------
    source:
        Original doc text.
    tagged:
        The LLM's rewrite of `source` with PII wrapped in `<LABEL>...</LABEL>` tags.

    Returns
    -------
    list[Span]
        Spans in `source` offsets. Raises `AlignmentError` when the untagged rewrite
        drifted too far from `source` to align.
    """
    raise NotImplementedError
