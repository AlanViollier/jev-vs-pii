"""results.md: every table for every dataset split of a scored run."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Sequence

from pii_bench.report.tables import cost_table, hits_table, paired_table, results_table
from pii_bench.schema import Hits, ResultRow

## Fine ai4privacy labels with fewer gold words than this in the split are left out.
_MIN_LABEL_WORDS = 30


def results_markdown(rows: Sequence[ResultRow], seed: int = 0) -> str:
    """Per dataset split: the headline, how sure the gaps are, cost, where each lane leaks, details.

    Parameters
    ----------
    rows:
        Every scored row of a run.
    seed:
        Bootstrap seed for the paired comparisons.

    Returns
    -------
    str
        The whole results page.
    """
    grouped: dict[tuple[str, str], list[ResultRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.dataset, row.split)].append(row)
    sections = []
    for (dataset, split), group in sorted(grouped.items()):
        headline = [row for row in group if row.headline]
        word = [row for row in headline if row.mode == "word"]
        sizes = ", ".join(sorted({f"{row.n_docs} docs" for row in word}))
        sections += [
            f"## {dataset} · {split} ({sizes})",
            "### Word level (headline; per-word lanes use the decoder that won on dev)",
            results_table(word),
        ]
        jev = [row for row in word if row.lane.family == "jev"]
        if jev:
            best_jev = max(jev, key=lambda row: row.scores.f2)
            others = [row for row in word if row.lane.family != "human"]
            sections += [
                f"### Every lane against {best_jev.name}, same docs (paired bootstrap)",
                paired_table(others, best_jev, seed),
            ]
        sections += [
            "### Cost and time per doc",
            cost_table([row for row in word if row.lane.family != "human"]),
            "### Recall by gold type (word level)",
            hits_table(word, lambda row: row.gold_by_type),
        ]
        if dataset == "tab":
            sections += [
                "### Recall by masking need: DIRECT identifiers vs QUASI (combine to re-identify)",
                hits_table(word, _regrouped(lambda detail: detail.split()[0])),
                "### Recall by TAB entity type",
                hits_table(word, _regrouped(lambda detail: detail.split()[1])),
            ]
        else:
            sections += [
                f"### Recall by ai4privacy label (labels with ≥ {_MIN_LABEL_WORDS} gold words)",
                hits_table(word, lambda row: row.gold_by_detail, min_total=_MIN_LABEL_WORDS),
            ]
        sections += [
            "### Precision by the type a lane claims (typed lanes)",
            hits_table(
                [row for row in word if row.predicted_by_type], lambda row: row.predicted_by_type
            ),
            "### Exact span match",
            results_table([row for row in headline if row.mode == "exact"]),
        ]
        decoded = [row for row in group if row.mode == "word" and row.lane.family == "jev"]
        if decoded:
            sections += [
                "### Every decoder on the Jev word scores (word level)",
                results_table(decoded),
            ]
        if dataset == "tab":
            sections += ["### Most leaked and most over-masked strings", _errors(word)]
    return "\n\n".join(sections) + "\n"


def _regrouped(group_of: Callable[[str], str]) -> Callable[[ResultRow], dict[str, Hits]]:
    """Sum a row's per-label counts into coarser groups of its dataset labels."""

    def hits(row: ResultRow) -> dict[str, Hits]:
        found: Counter[str] = Counter()
        total: Counter[str] = Counter()
        for detail, (hit, count) in row.gold_by_detail.items():
            found[group_of(detail)] += hit
            total[group_of(detail)] += count
        return {group: (found[group], total[group]) for group in total}

    return hits


def _errors(rows: Sequence[ResultRow]) -> str:
    lines = []
    for row in sorted(rows, key=lambda row: row.scores.f2, reverse=True):
        if row.lane.family in ("human", "baseline"):
            continue
        missed = ", ".join(f"{text} ({n})" for text, n in row.top_missed[:8]) or "–"
        alarms = ", ".join(f"{text} ({n})" for text, n in row.top_false_alarms[:8]) or "–"
        lines.append(f"- → **{row.name}** leaks: {missed}  \n  over-masks: {alarms}")
    return "\n".join(lines)
