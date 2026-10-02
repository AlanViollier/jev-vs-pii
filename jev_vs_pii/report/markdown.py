"""results.md: every table for every dataset split of a scored run."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Sequence

from jev_vs_pii.report.tables import cost_table, hits_table, paired_table, results_table
from jev_vs_pii.schema import Hits, ResultRow

## Fine dataset labels with fewer gold words than this in the split are left out as noise.
_MIN_LABEL_WORDS = 30
## What a reader must know before comparing a lane's headline number, per dataset.
_CAVEATS: dict[str, list[tuple[str, str]]] = {
    "ai4privacy": [
        (
            "privacy_filter",
            "OpenAI reports Privacy Filter results on pii-masking-300k, this set's source.",
        ),
    ],
    "nemotron": [
        (
            "gliner_pii",
            "GLiNER-PII was trained on Nemotron-PII's train split. Test samples the test file; "
            "dev samples train, so GLiNER's dev score and tuned threshold come from its own "
            "training data.",
        ),
    ],
}
_ALWAYS = [
    (
        "privacy_filter",
        "Privacy Filter has 8 categories: no organisations, demographics or most IDs.",
    ),
    ("llm_", "An LLM answer that is cut off or won't parse counts as finding nothing (`failed`)."),
]


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
            "### Word level (headline; per-word lanes use a threshold tuned on dev)",
            results_table(word),
            _caveats(dataset, word),
        ]
        decision = [row for row in word if row.lane.family == "decision"]
        if decision:
            best = max(decision, key=lambda row: row.scores.f2)
            others = [row for row in word if row.lane.family != "human"]
            sections += [
                f"### Every lane against {best.name}, same docs (paired bootstrap)",
                paired_table(others, best, seed),
            ]
        sections += [
            "### Format vs context: recall on PII found by its form vs by its meaning",
            _shape_table(word),
            "### Cost and time per doc",
            cost_table([row for row in word if row.lane.family != "human"]),
            "### Recall by gold type (word level)",
            hits_table(word, lambda row: row.gold_by_type),
        ]
        if dataset == "tab":
            sections += [
                "### TAB's official script (entity recall on direct / quasi identifiers, token P/R/F1)",
                _official_table(word),
                "### Recall by masking need: DIRECT identifiers vs QUASI (combine to re-identify)",
                hits_table(word, _regrouped(lambda detail: detail.split()[0])),
                "### Recall by TAB entity type",
                hits_table(word, _regrouped(lambda detail: detail.split()[1])),
            ]
        else:
            sections += [
                f"### Recall by {dataset} label (labels with ≥ {_MIN_LABEL_WORDS} gold words)",
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
        ## Lanes that score words have calibration; every decoder was tried on their scores.
        scorers = {row.lane.id for row in group if row.ece is not None}
        decoded = [row for row in group if row.mode == "word" and row.lane.id in scorers]
        if decoded:
            sections += [
                "### Every decoder on per-word scores (word level)",
                results_table(decoded),
            ]
        if any(row.top_missed or row.top_false_alarms for row in word):
            sections += ["### Most leaked and most over-masked strings", _errors(word)]
    return "\n\n".join(sections) + "\n"


def _caveats(dataset: str, rows: Sequence[ResultRow]) -> str:
    """Notes for the lanes in this table whose number needs context to read."""
    ids = {row.lane.id for row in rows}
    notes = [
        note
        for prefix, note in [*_CAVEATS.get(dataset, []), *_ALWAYS]
        if any(lane_id.startswith(prefix) for lane_id in ids)
    ]
    return "\n".join(f"- → {note}" for note in notes)


def _official_table(rows: Sequence[ResultRow]) -> str:
    """TAB's own measures per lane, in the names its paper uses."""
    columns = {
        "recall_direct_entities": "ER direct",
        "recall_quasi_entities": "ER quasi",
        "token_recall": "token R",
        "token_precision": "token P",
        "token_f1": "token F1",
    }
    lines = [
        f"| lane | {' | '.join(columns.values())} |",
        f"|---|{'---|' * len(columns)}",
    ]
    for row in sorted(rows, key=lambda row: row.scores.f2, reverse=True):
        if row.tab_official is None:
            continue
        values = " | ".join(f"{row.tab_official[name]:.3f}" for name in columns)
        lines.append(f"| {row.name} | {values} |")
    return "\n".join(lines)


def _shape_table(rows: Sequence[ResultRow]) -> str:
    """Recall on format-shaped vs context-shaped gold, plus TAB's context over-masking."""
    cleared = any(row.cleared_masked for row in rows)
    header = "| lane | format recall | context recall | gap |"
    header += " left-in-clear masked (lower is better) |" if cleared else ""
    lines = [header, "|---|---|---|---|" + ("---|" if cleared else "")]
    for row in sorted(rows, key=lambda row: row.scores.f2, reverse=True):
        format_recall = _ratio(row.gold_by_shape.get("format"))
        context_recall = _ratio(row.gold_by_shape.get("context"))
        gap = (
            f"{format_recall - context_recall:+.2f}"
            if format_recall is not None and context_recall is not None
            else "–"
        )
        line = f"| {row.name} | {_fmt(format_recall)} | {_fmt(context_recall)} | {gap} |"
        if cleared:
            line += f" {_fmt(_ratio(row.cleared_masked))} |"
        lines.append(line)
    return "\n".join(lines)


def _ratio(hits: Hits | None) -> float | None:
    return hits[0] / hits[1] if hits and hits[1] else None


def _fmt(value: float | None) -> str:
    return "–" if value is None else f"{value:.2f}"


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
