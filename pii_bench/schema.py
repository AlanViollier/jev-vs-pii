"""Typed objects every module passes around: words, spans, docs, predictions, scores."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

Dataset = Literal["ai4privacy", "tab"]
Split = Literal["dev", "test"]
Tier = Literal["smoke", "pilot", "full"]
Family = Literal["rules", "ner", "jev", "llm", "cascade"]
Residency = Literal["local", "eu_hosted", "us_gdpr_agreement"]
MatchMode = Literal["word", "exact"]


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
    """A predicted or gold PII span. `label` is the coarse type when known; `score` when the method has one."""

    start: int = Field(ge=0)
    end: int
    label: str | None = None
    score: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _non_empty(self) -> Self:
        if self.end <= self.start:
            raise ValueError(f"span end {self.end} must be after start {self.start}")
        return self


class Doc(_Frozen):
    """One gold document. `gold` is the primary annotation; `other_annotators` holds TAB's extra ones.

    `subject` is the person TAB asks to protect; its gold only masks what re-identifies them.
    """

    id: str
    dataset: Dataset
    split: Split
    text: str
    gold: tuple[Span, ...]
    other_annotators: tuple[tuple[Span, ...], ...] = ()
    subject: str | None = None

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


class LaneInfo(_Frozen):
    """Identity of a lane, carried into every result row."""

    id: str
    family: Family
    residency: Residency
    model: str | None = None


class Prediction(_Frozen):
    """One lane's output on one doc. `word_scores` aligns with `split_words(doc.text)` when present."""

    doc_id: str
    lane_id: str
    spans: tuple[Span, ...]
    word_scores: tuple[WordScore, ...] | None = None
    usage: Usage = Usage()


class LaneRun(_Frozen):
    """Every prediction one lane made on one dataset split in one run."""

    run_id: str
    lane: LaneInfo
    dataset: Dataset
    split: Split
    tier: Tier
    started_at: datetime
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
    """Cost and latency of a lane run, normalised per document."""

    usd_per_1k_docs: Decimal
    calls_per_doc: float
    latency_p50_s: float
    latency_p95_s: float
    wall_clock_s: float


class ResultRow(_Frozen):
    """One row of the results table: a lane on a dataset split, scored."""

    lane: LaneInfo
    dataset: Dataset
    split: Split
    mode: MatchMode
    scores: SpanScores
    f2_ci: tuple[float, float]
    cost: CostSummary
    ece: float | None = None
