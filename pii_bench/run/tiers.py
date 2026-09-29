"""Ramp tiers: smoke proves a lane runs, pilot checks the numbers, full is the sweep."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.schema import Doc, Tier

TIER_SIZES: dict[Tier, int | None] = {"smoke": 2, "pilot": 20, "full": None}


def select_docs(docs: Sequence[Doc], tier: Tier) -> list[Doc]:
    """Take the first docs of a stable order, so each tier is a prefix of the next.

    Parameters
    ----------
    docs:
        The loaded split, already in stable order.
    tier:
        Which ramp step.

    Returns
    -------
    list[Doc]
        A prefix: pilot reuses every smoke response from the cache, full reuses pilot's.
    """
    return list(docs[: TIER_SIZES[tier]])
