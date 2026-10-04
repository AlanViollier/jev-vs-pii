"""Small JSON files for charts and the demo page, from a scored run. What `docs/data/` holds.

Each file is flat records, ready to hand to a chart tool: `headline` (one row per lane and
dataset), `paired` (every lane against the best decision lane, same docs), `curves` (calibration
and threshold curves of the per-word lanes), `per_doc` (cost and time against doc length)
and `examples` (a few whole docs with every lane's spans, for the side-by-side views).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from jev_vs_pii.decode import DecodeParams, decode
from jev_vs_pii.metrics.bootstrap import paired_f2_diff
from jev_vs_pii.metrics.spans import DocCounts, doc_counts
from jev_vs_pii.schema import Dataset, Doc, Hits, LaneRun, ResultRow, Span
from jev_vs_pii.words import covering_spans, split_words

## ai4privacy's licence forbids showing its text, so examples come from these only.
EXAMPLE_DATASETS: tuple[Dataset, ...] = ("tab", "nemotron")
## The first docs of each test split in its stable order: no picking the ones that look good.
EXAMPLES_PER_DATASET = 5

Record = dict[str, Any]


def headline_records(rows: Sequence[ResultRow]) -> list[Record]:
    """One record per lane and dataset: the numbers of its headline word-level row."""
    return [
        {
            "dataset": row.dataset,
            "lane": row.lane.id,
            "family": row.lane.family,
            "decoder": row.decoder,
            "n_docs": row.n_docs,
            "f2": row.scores.f2,
            "f2_low": row.f2_ci[0],
            "f2_high": row.f2_ci[1],
            "precision": row.scores.precision,
            "recall": row.scores.recall,
            "f1": row.scores.f1,
            "leaked": row.leaked,
            "docs_without_leak": row.docs_without_leak,
            "ece": row.ece,
            "usd_per_1k_docs": float(row.cost.usd_per_1k_docs),
            "latency_p50_s": row.cost.latency_p50_s,
            "latency_p95_s": row.cost.latency_p95_s,
            "failed": row.failed,
            "dropped": row.dropped,
            "format_recall": _ratio(row.gold_by_shape.get("format")),
            "context_recall": _ratio(row.gold_by_shape.get("context")),
            "cleared_masked": _ratio(row.cleared_masked),
            "recall_by_type": {label: _ratio(hits) for label, hits in row.gold_by_type.items()},
            "tab_official": row.tab_official,
        }
        for row in _headline(rows)
    ]


def paired_records(rows: Sequence[ResultRow], seed: int = 0) -> list[Record]:
    """Every lane's F2 minus the best decision lane's, on the same docs, with a paired 95% CI."""
    records = []
    headline = _headline(rows)
    for dataset in sorted({row.dataset for row in headline}):
        group = [row for row in headline if row.dataset == dataset]
        decision = [row for row in group if row.lane.family == "decision"]
        if not decision:
            continue
        reference = max(decision, key=lambda row: row.scores.f2)
        theirs = {doc.doc_id: doc for doc in reference.per_doc}
        for row in group:
            if row is reference or row.lane.family == "human":
                continue
            shared = [doc for doc in row.per_doc if doc.doc_id in theirs]
            diff, low, high = paired_f2_diff(
                [DocCounts(doc.tp, doc.fp, doc.fn) for doc in shared],
                [
                    DocCounts(theirs[d.doc_id].tp, theirs[d.doc_id].fp, theirs[d.doc_id].fn)
                    for d in shared
                ],
                seed=seed,
            )
            records.append(
                {
                    "dataset": dataset,
                    "lane": row.lane.id,
                    "reference": reference.lane.id,
                    "f2_diff": diff,
                    "low": low,
                    "high": high,
                }
            )
    return records


def curve_records(rows: Sequence[ResultRow]) -> list[Record]:
    """Reliability bins and threshold curves of every lane that scores words."""
    return [
        {
            "dataset": row.dataset,
            "lane": row.lane.id,
            "reliability": [b.model_dump() for b in row.reliability or ()],
            "threshold_curve": [p.model_dump() for p in row.threshold_curve or ()],
        }
        for row in rows
        if row.mode == "word" and row.threshold_curve
    ]


def per_doc_records(rows: Sequence[ResultRow]) -> list[Record]:
    """Each paid lane's cost and latency on every doc, against the doc's length in words."""
    return [
        {
            "dataset": row.dataset,
            "lane": row.lane.id,
            "n_words": [doc.n_words for doc in row.per_doc],
            "cost_usd": [float(doc.cost_usd) for doc in row.per_doc],
            "latency_s": [round(doc.latency_s, 3) for doc in row.per_doc],
        }
        for row in _headline(rows)
        if row.lane.family in ("decision", "llm")
    ]


def example_records(
    lane_runs: Sequence[LaneRun],
    docs: Mapping[Dataset, Sequence[Doc]],
    decoders: Mapping[tuple[str, Dataset], DecodeParams],
) -> list[Record]:
    """The first docs of each showable test split, with gold and every lane's spans on them.

    Parameters
    ----------
    lane_runs:
        Test-split lane runs.
    docs:
        Each dataset's test docs in their stable order.
    decoders:
        (lane id, dataset) -> the headline decoder, for lanes that score words.

    Returns
    -------
    list[Record]
        One record per doc: text, words, gold and which words it covers, cleared, and per
        lane its spans, which words they mask, word-level tp / fp / fn, per-word probability
        when it has one, latency, cost, failure and raw answer.
    """
    records = []
    for dataset in EXAMPLE_DATASETS:
        runs = [run for run in lane_runs if run.dataset == dataset and run.split == "test"]
        for doc in docs.get(dataset, [])[:EXAMPLES_PER_DATASET]:
            words = split_words(doc.text)
            lanes: dict[str, Record] = {}
            for run in runs:
                found = [p for p in run.predictions if p.doc_id == doc.id]
                if not found:
                    continue
                prediction = found[0]
                decoder = decoders.get((run.lane.id, dataset))
                spans = (
                    decode(words, prediction.word_scores, decoder)
                    if decoder is not None and prediction.word_scores is not None
                    else prediction.spans
                )
                counts = doc_counts(doc, spans, "word")
                lanes[run.lane.id] = {
                    "spans": [_span(span) for span in spans],
                    "masked": [span is not None for span in covering_spans(words, spans)],
                    "tp": counts.tp,
                    "fp": counts.fp,
                    "fn": counts.fn,
                    "p_pii": [round(s.p_pii, 3) for s in prediction.word_scores]
                    if prediction.word_scores is not None
                    else None,
                    "latency_s": prediction.usage.latency_s,
                    "cost_usd": float(prediction.usage.cost_usd),
                    "failure": prediction.failure,
                    "answer": prediction.answer,
                }
            records.append(
                {
                    "dataset": dataset,
                    "doc_id": doc.id,
                    "text": doc.text,
                    "words": [[word.start, word.end] for word in words],
                    "gold": [_span(span) for span in doc.gold],
                    "gold_words": [span is not None for span in covering_spans(words, doc.gold)],
                    "cleared": [_span(span) for span in doc.cleared],
                    "lanes": lanes,
                }
            )
    return records


def _headline(rows: Sequence[ResultRow]) -> list[ResultRow]:
    return [row for row in rows if row.headline and row.mode == "word"]


def _span(span: Span) -> Record:
    return {"start": span.start, "end": span.end, "label": span.label, "detail": span.detail}


def _ratio(hits: Hits | None) -> float | None:
    return hits[0] / hits[1] if hits and hits[1] else None
