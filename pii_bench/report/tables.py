"""Results as Markdown tables for the README and run folders."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.schema import ResultRow
from pii_bench.taxonomy import DEFINITIONS


def results_table(rows: Sequence[ResultRow]) -> str:
    """One row per lane, best F2 first: F2 with its 95% CI, P, R, calibration, cost, failures.

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split and match mode.

    Returns
    -------
    str
        A Markdown table.
    """
    header = (
        "| lane | F2 [95% CI] | P | R | ECE | $/1k docs | calls/doc | p50 s | failed |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    lines = [
        f"| {row.name} "
        f"| {row.scores.f2:.3f} [{row.f2_ci[0]:.3f}, {row.f2_ci[1]:.3f}] "
        f"| {row.scores.precision:.3f} | {row.scores.recall:.3f} "
        f"| {_maybe(row.ece)} "
        f"| {row.cost.usd_per_1k_docs:.3f} | {row.cost.calls_per_doc:.1f} "
        f"| {row.cost.latency_p50_s:.2f} "
        f"| {_failures(row)} |"
        for row in _by_f2(rows)
    ]
    return "\n".join([header, *lines])


def recall_by_type_table(rows: Sequence[ResultRow]) -> str:
    """Word-level recall per gold type, one row per lane: where each method leaks.

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split (word mode).

    Returns
    -------
    str
        A Markdown table; a dash where the split has no gold of that type.
    """
    types = [label for label in DEFINITIONS if any(label in row.recall_by_type for row in rows)]
    header = f"| lane | {' | '.join(types)} |\n|---|{'---|' * len(types)}"
    lines = [
        f"| {row.name} | "
        + " | ".join(_maybe(row.recall_by_type.get(label)) for label in types)
        + " |"
        for row in _by_f2(rows)
    ]
    return "\n".join([header, *lines])


def _by_f2(rows: Sequence[ResultRow]) -> list[ResultRow]:
    return sorted(rows, key=lambda row: row.scores.f2, reverse=True)


def _maybe(value: float | None) -> str:
    return "–" if value is None else f"{value:.3f}"


def _failures(row: ResultRow) -> str:
    """Unusable answers, plus items that couldn't be placed in the text when there are any."""
    return f"{row.failed} (+{row.dropped} dropped)" if row.dropped else str(row.failed)
