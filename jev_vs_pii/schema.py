"""Typed objects every module passes around: words, spans, docs, predictions, scores."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Dataset = Literal["ai4privacy", "tab", "nemotron"]
Split = Literal["dev", "test"]
Tier = Literal["smoke", "pilot", "full"]
Family = Literal["baseline", "human", "rules", "ner", "decision", "llm"]
MatchMode = Literal["word", "exact"]
## Why a generative lane's answer was unusable.
Failure = Literal["truncated", "unparseable", "misaligned"]
## (hits, total): kept as counts so any grouping can be re-aggregated later.
Hits = tuple[int, int]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Word(_Frozen):
    """One whitespace token with edge punctuation trimmed, located by character offsets."""

    text: str
    start: int = Field(ge=0)
    end: int

    @model_validator(mode="after")
    def _non_empty(self) -> Self:
        if self.end <= self.start:
            raise ValueError(f"word end {self.end} must be after start {self.start}")
        return self


class Span(_Frozen):
    """A predicted or gold PII span. `label` is the coarse type when known; `score` when the method has one.

    `detail` keeps a gold span's own dataset label (`LASTNAME1`, `QUASI DATETIME`) for fine breakdowns.
    """

    start: int = Field(ge=0)
    end: int
    label: str | None = None
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    detail: str | None = None

    @model_validator(mode="after")
    def _non_empty(self) -> Self:
        if self.end <= self.start:
            raise ValueError(f"span end {self.end} must be after start {self.start}")
        return self


class Doc(_Frozen):
    """One gold document. `gold` is the primary annotation; `other_annotators` holds TAB's extra ones.

    `subject` is the person TAB asks to protect; its gold only masks what re-identifies them.
    `cleared` holds entities the annotator marked and decided need no masking (TAB's NO_MASK):
    masking them is the over-masking that only context can avoid.
    """

    id: str
    dataset: Dataset
    split: Split
    text: str
    gold: tuple[Span, ...]
    other_annotators: tuple[tuple[Span, ...], ...] = ()
    subject: str | None = None
    cleared: tuple[Span, ...] = ()

    @model_validator(mode="after")
    def _tab_names_its_subject(self) -> Self:
        if self.dataset == "tab" and not self.subject:
            raise ValueError(f"TAB doc {self.id} needs the subject its gold protects")
        return self


class WordScore(_Frozen):
    """What a per-word scorer says about one word.

    `p_continue` is set by lanes that ask whether the word continues the previous item;
    `label_probs` by lanes that ask for a type per word.
    """

    p_pii: float = Field(ge=0.0, le=1.0)
    p_continue: float | None = Field(default=None, ge=0.0, le=1.0)
    label_probs: dict[str, float] | None = None


class Usage(_Frozen):
    """Cost and time spent producing one prediction."""

    calls: int = 0
    cache_hits: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: Decimal = Decimal(0)
    latency_s: float = 0.0

    @classmethod
    def combine(cls, usages: Sequence[Usage]) -> Usage:
        """Total of calls made concurrently for one doc: counts and cost add, latency is the slowest."""
        return cls(
            calls=sum(u.calls for u in usages),
            cache_hits=sum(u.cache_hits for u in usages),
            input_tokens=sum(u.input_tokens for u in usages),
            output_tokens=sum(u.output_tokens for u in usages),
            cost_usd=sum((u.cost_usd for u in usages), Decimal(0)),
            latency_s=max((u.latency_s for u in usages), default=0.0),
        )


class LaneInfo(_Frozen):
    """Identity of a lane, carried into every result row."""

    id: str
    family: Family
    model: str | None = None


class Prediction(_Frozen):
    """One lane's output on one doc. `word_scores` aligns with `split_words(doc.text)` when present.

    `failure` says why an answer was unusable (it then scores as finding nothing); `dropped`
    counts items in a usable answer that couldn't be placed in the text. Generative lanes
    keep their raw `answer` and the `provider` that served it.
    """

    doc_id: str
    lane_id: str
    spans: tuple[Span, ...]
    word_scores: tuple[WordScore, ...] | None = None
    usage: Usage = Usage()
    failure: Failure | None = None
    dropped: int = 0
    answer: str | None = None
    provider: str | None = None

    @property
    def failed(self) -> bool:
        """The lane got no usable answer for this doc."""
        return self.failure is not None


class LaneRun(_Frozen):
    """Every prediction one lane made on one dataset split in one run."""

    run_id: str
    lane: LaneInfo
    dataset: Dataset
    split: Split
    tier: Tier
    started_at: datetime
    wall_clock_s: float
    predictions: tuple[Prediction, ...]


class SpanScores(_Frozen):
    """Span-level counts and the scores derived from them."""

    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float
    f2: float


class CostSummary(_Frozen):
    """Cost, time and tokens of a lane run, normalised per document."""

    usd_per_1k_docs: Decimal
    calls_per_doc: float
    input_tokens_per_doc: float
    output_tokens_per_doc: float
    latency_mean_s: float
    latency_p50_s: float
    latency_p95_s: float
    wall_clock_s: float


class DocResult(_Frozen):
    """One doc's outcome for one lane: counts in the row's match mode, plus what it cost."""

    doc_id: str
    n_words: int
    tp: int
    fp: int
    fn: int
    cost_usd: Decimal
    latency_s: float
    input_tokens: int
    output_tokens: int
    failed: bool
    dropped: int


class CurvePoint(_Frozen):
    """Word-level precision, recall and F2 when every word at or above `cutoff` is masked."""

    cutoff: float
    precision: float
    recall: float
    f2: float


class ReliabilityBin(_Frozen):
    """One confidence bucket: mean confidence vs how often it was right."""

    low: float
    high: float
    count: int
    mean_confidence: float
    accuracy: float


class ResultRow(_Frozen):
    """One row of the results: a lane on a dataset split, scored in one match mode.

    `decoder` names how per-word scores became spans (`None`: the lane's own spans);
    `headline` marks the one row per lane the results lead with (for per-word lanes, the
    threshold tuned on dev). Hit counts are words: gold words by gold type, dataset label or
    shape (format / context), predicted words by predicted type, and for TAB the words of
    entities left in clear that the lane masked anyway. `per_doc` feeds paired comparisons and plots;
    `reliability` and `threshold_curve` exist for lanes that score words; the top error
    strings are kept for TAB only, whose licence allows showing its text; `tab_official`
    holds TAB's own evaluation script's measures on a headline TAB row.
    """

    lane: LaneInfo
    decoder: str | None = None
    headline: bool = True
    dataset: Dataset
    split: Split
    mode: MatchMode
    n_docs: int
    scores: SpanScores
    f2_ci: tuple[float, float]
    cost: CostSummary
    ece: float | None = None
    brier: float | None = None
    gold_by_type: dict[str, Hits]
    gold_by_detail: dict[str, Hits]
    gold_by_shape: dict[str, Hits]
    predicted_by_type: dict[str, Hits]
    cleared_masked: Hits | None = None
    failed: int
    dropped: int
    per_doc: tuple[DocResult, ...]
    reliability: tuple[ReliabilityBin, ...] | None = None
    threshold_curve: tuple[CurvePoint, ...] | None = None
    top_missed: tuple[tuple[str, int], ...] = ()
    top_false_alarms: tuple[tuple[str, int], ...] = ()
    tab_official: dict[str, float] | None = None

    @property
    def name(self) -> str:
        """Lane id, with the decoder when it isn't the lane's own."""
        return f"{self.lane.id} · {self.decoder}" if self.decoder else self.lane.id
