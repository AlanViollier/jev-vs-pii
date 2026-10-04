"""Results as Markdown tables for the README and run folders."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence

from jev_vs_pii.metrics.bootstrap import paired_f2_diff
from jev_vs_pii.metrics.spans import DocCounts
from jev_vs_pii.schema import Hits, ResultRow

HitsOf = Callable[[ResultRow], dict[str, Hits]]


def results_table(rows: Sequence[ResultRow]) -> str:
    """One row per lane, best F2 first: F2 with its 95% CI, P, R, F1, leaks, calibration, cost, failures.

    `frontier` marks lanes no other lane beats on both F2 and cost (the human row aside).

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split and match mode.

    Returns
    -------
    str
        A Markdown table.
    """
    frontier = pareto_frontier(rows)
    header = (
        "| lane | F2 [95% CI] | P | R | F1 | leaked | docs, no leak | ECE | $/1k docs | p50 s "
        "| failed | frontier |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|"
    )
    lines = [
        f"| {row.name} "
        f"| {row.scores.f2:.3f} [{row.f2_ci[0]:.3f}, {row.f2_ci[1]:.3f}] "
        f"| {row.scores.precision:.3f} | {row.scores.recall:.3f} | {row.scores.f1:.3f} "
        f"| {row.leaked:.1%} | {_percent(row.docs_without_leak)} | {_maybe(row.ece)} | {row.cost.usd_per_1k_docs:.3f} | {row.cost.latency_p50_s:.2g} "
        f"| {_failures(row)} | {'yes' if row.name in frontier else ''} |"
        for row in _by_f2(rows)
    ]
    return "\n".join([header, *lines])


def cost_table(rows: Sequence[ResultRow]) -> str:
    """What each lane spends per doc: money, calls, tokens, time.

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split (one mode is enough; cost doesn't depend on it).

    Returns
    -------
    str
        A Markdown table, cheapest first.
    """
    header = (
        "| lane | $/1k docs | calls/doc | tokens in/doc | tokens out/doc "
        "| latency mean s | p50 s | p95 s | wall clock s |\n"
        "|---|---|---|---|---|---|---|---|---|"
    )
    lines = [
        f"| {row.name} | {c.usd_per_1k_docs:.3f} | {c.calls_per_doc:.1f} "
        f"| {c.input_tokens_per_doc:,.0f} | {c.output_tokens_per_doc:,.0f} "
        f"| {c.latency_mean_s:.2g} | {c.latency_p50_s:.2g} | {c.latency_p95_s:.2g} "
        f"| {c.wall_clock_s:.0f} |"
        for row in sorted(rows, key=lambda row: row.cost.usd_per_1k_docs)
        for c in [row.cost]
    ]
    return "\n".join([header, *lines])


def hits_table(rows: Sequence[ResultRow], hits_of: HitsOf, min_total: int = 1) -> str:
    """Share of hits per group, one row per lane: recall per gold type, precision per claimed type.

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split (word mode).
    hits_of:
        Which counts to show, e.g. `lambda row: row.gold_by_type`.
    min_total:
        Leave out groups with fewer words than this across the split (rare labels are noise).

    Returns
    -------
    str
        A Markdown table, a dash where a lane has no words in that group; one line instead
        when no group is big enough.
    """
    totals: Counter[str] = Counter()
    for row in rows:
        for group, (_, total) in hits_of(row).items():
            totals[group] = max(totals[group], total)
    groups = sorted(group for group, total in totals.items() if total >= min_total)
    if not groups:
        return f"No group has {min_total} or more words on this split."
    header = f"| lane | {' | '.join(groups)} |\n|---|{'---|' * len(groups)}"
    lines = [
        f"| {row.name} | " + " | ".join(_share(hits_of(row).get(group)) for group in groups) + " |"
        for row in _by_f2(rows)
    ]
    return "\n".join([header, *lines])


def paired_table(rows: Sequence[ResultRow], reference: ResultRow, seed: int = 0) -> str:
    """Every lane against one reference lane on the same docs: F2 difference with a paired 95% CI.

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split and match mode.
    reference:
        The lane the others are compared to.
    seed:
        Bootstrap seed.

    Returns
    -------
    str
        A Markdown table; `yes` where the interval excludes zero.
    """
    header = f"| lane | F2 − {reference.name} [95% CI] | clear gap |\n|---|---|---|"
    lines = []
    for row in _by_f2(rows):
        if row is reference:
            continue
        mine, theirs = _aligned(row, reference)
        diff, low, high = paired_f2_diff(mine, theirs, seed=seed)
        clear = "yes" if low > 0 or high < 0 else ""
        lines.append(f"| {row.name} | {diff:+.3f} [{low:+.3f}, {high:+.3f}] | {clear} |")
    return "\n".join([header, *lines])


def pareto_frontier(rows: Sequence[ResultRow]) -> set[str]:
    """Names of lanes that no other lane beats on F2 without costing more."""
    lanes = [row for row in rows if row.lane.family != "human"]
    return {
        row.name
        for row in lanes
        if not any(
            other.cost.usd_per_1k_docs <= row.cost.usd_per_1k_docs
            and other.scores.f2 > row.scores.f2
            for other in lanes
        )
    }


def _aligned(a: ResultRow, b: ResultRow) -> tuple[list[DocCounts], list[DocCounts]]:
    """Per-doc counts of both rows on the docs they share, in the same order."""
    theirs = {doc.doc_id: doc for doc in b.per_doc}
    shared = [doc for doc in a.per_doc if doc.doc_id in theirs]
    return (
        [DocCounts(doc.tp, doc.fp, doc.fn) for doc in shared],
        [
            DocCounts(theirs[doc.doc_id].tp, theirs[doc.doc_id].fp, theirs[doc.doc_id].fn)
            for doc in shared
        ],
    )


def _by_f2(rows: Sequence[ResultRow]) -> list[ResultRow]:
    return sorted(rows, key=lambda row: row.scores.f2, reverse=True)


def _maybe(value: float | None) -> str:
    return "–" if value is None else f"{value:.3f}"


def _share(hits: Hits | None) -> str:
    return "–" if not hits or not hits[1] else f"{hits[0] / hits[1]:.2f}"


def _failures(row: ResultRow) -> str:
    """Unusable answers, plus items that couldn't be placed in the text when there are any."""
    return f"{row.failed} (+{row.dropped} dropped)" if row.dropped else str(row.failed)


def _percent(value: float | None) -> str:
    return "–" if value is None else f"{value:.0%}"
