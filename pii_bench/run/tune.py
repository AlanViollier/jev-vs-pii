"""Pick decoder knobs on the dev split, by word-level F2. Never on test."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, TypeAdapter

from pii_bench.decode import Closing, DecodeParams, Hysteresis, Threshold, Viterbi, decode
from pii_bench.metrics.spans import doc_counts, scores_from_counts
from pii_bench.schema import Dataset, Doc, LaneRun
from pii_bench.words import split_words

## Finer at the bottom: small PII models put real hits at scores of a few percent.
_CUTOFFS = [0.01, 0.02, 0.03, *(round(0.05 * step, 2) for step in range(1, 20))]

## Every decoder with a coarse grid over its knobs; tuning picks the best of each kind.
GRID: dict[str, list[DecodeParams]] = {
    "threshold": [Threshold(cutoff=c) for c in _CUTOFFS],
    "hysteresis": [
        Hysteresis(high=high, low=low)
        for high in _CUTOFFS[7::2]
        for low in _CUTOFFS[::2]
        if low < high
    ],
    "closing": [Closing(cutoff=c, gap=gap) for c in _CUTOFFS for gap in (1, 2)],
    "viterbi": [
        Viterbi(cutoff=c, switch_cost=cost)
        for c in _CUTOFFS[::2]
        for cost in (0.25, 0.5, 1.0, 2.0, 4.0)
    ],
}


def tune_lane_run(lane_run: LaneRun, docs: Sequence[Doc]) -> dict[str, tuple[DecodeParams, float]]:
    """Best settings of each decoder kind for one per-word lane run on dev.

    Parameters
    ----------
    lane_run:
        A dev-split run whose predictions carry `word_scores`.
    docs:
        The dev docs.

    Returns
    -------
    dict[str, tuple[DecodeParams, float]]
        Decoder kind -> best settings and their dev word-level F2. Raises `ValueError`
        on a test-split run or one without word scores.
    """
    if lane_run.split != "dev":
        raise ValueError(
            f"{lane_run.lane.id}: decoders are tuned on dev only, got {lane_run.split}"
        )
    by_id = {doc.id: doc for doc in docs}
    scored = [(by_id[p.doc_id], p.word_scores) for p in lane_run.predictions]
    if any(scores is None for _, scores in scored):
        raise ValueError(f"{lane_run.lane.id}: no word scores to tune a decoder on")
    words = [split_words(doc.text) for doc, _ in scored]
    best: dict[str, tuple[DecodeParams, float]] = {}
    for kind, grid in GRID.items():
        for params in grid:
            counts = (
                doc_counts(doc, decode(doc_words, scores or (), params), "word")
                for (doc, scores), doc_words in zip(scored, words, strict=True)
            )
            f2 = scores_from_counts(counts).f2
            if kind not in best or f2 > best[kind][1]:
                best[kind] = (params, f2)
    return best


class TunedDecoder(BaseModel):
    """A decoder's tuned settings and the dev F2 that picked them."""

    params: DecodeParams
    dev_f2: float


## lane id -> dataset -> the best settings of each decoder kind, best dev F2 first.
Tuned = dict[str, dict[Dataset, list[TunedDecoder]]]
_TUNED = TypeAdapter(Tuned)


def ranked(best: dict[str, tuple[DecodeParams, float]]) -> list[TunedDecoder]:
    """Tuning results as stored: best dev F2 first, so the headline decoder is chosen on dev."""
    decoders = [TunedDecoder(params=params, dev_f2=f2) for params, f2 in best.values()]
    return sorted(decoders, key=lambda decoder: decoder.dev_f2, reverse=True)


def load_tuned(path: Path) -> Tuned:
    """Read tuned decoders; empty when nothing has been tuned yet."""
    return _TUNED.validate_json(path.read_bytes()) if path.exists() else {}


def save_tuned(path: Path, tuned: Tuned) -> None:
    """Write tuned decoders, replacing the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_TUNED.dump_json(tuned, indent=2))
