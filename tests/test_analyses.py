from __future__ import annotations

from datetime import datetime

import pytest

from jev_vs_pii.lanes import designs
from jev_vs_pii.metrics.results import score_lane_run
from jev_vs_pii.report.analyses import (
    analyses_markdown,
    answered_by_both,
    context_position,
)
from jev_vs_pii.schema import Doc, LaneInfo, LaneRun, Prediction, Span, WordScore
from jev_vs_pii.words import split_words

_TEXT = "Mail ann@example.org or call Ann Lee today."


def _doc(i: int = 0) -> Doc:
    return Doc(
        id=f"d{i}",
        dataset="tab",
        split="test",
        text=_TEXT,
        gold=(Span(start=5, end=20, label="CONTACT"), Span(start=29, end=36, label="PERSON")),
        subject="Ann Lee",
    )


def _run(predictions: list[Prediction], lane: str = "decision_words:jev") -> LaneRun:
    return LaneRun(
        run_id="r",
        lane=LaneInfo(id=lane, family="llm" if lane.startswith("llm") else "decision"),
        dataset="tab",
        split="test",
        tier="full",
        started_at=datetime(2026, 10, 1),
        wall_clock_s=1.0,
        predictions=tuple(predictions),
    )


def _scored(doc: Doc, probs: dict[str, float]) -> Prediction:
    scores = tuple(WordScore(p_pii=probs.get(w.text, 0.05)) for w in split_words(doc.text))
    return Prediction(doc_id=doc.id, lane_id="decision_words:jev", spans=(), word_scores=scores)


def test_context_position_splits_answers_at_the_limit() -> None:
    doc = _doc()
    run = _run([_scored(doc, {"Ann": 0.9})])
    early, late = context_position(run, [doc], limit=10**6)
    assert (early.words, late.words) == (7, 0) and late.brier is None
    early, late = context_position(run, [doc], limit=0)
    assert (early.words, late.words) == (0, 7)
    assert late.gold_share == 3 / 7


def test_context_position_leaves_out_words_never_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(designs, "_stop_words", lambda: frozenset({"or", "today"}))
    doc = _doc()
    run = _run([_scored(doc, {"Ann": 0.9})], "decision_typed_skip:jev")
    early, late = context_position(run, [doc], limit=10**6)
    assert (early.words, late.words) == (5, 0)


def test_answered_by_both_leaves_out_docs_either_lane_failed() -> None:
    docs = [_doc(0), _doc(1)]
    found = (Span(start=5, end=20), Span(start=29, end=36))
    a = _run([Prediction(doc_id=d.id, lane_id="llm_a", spans=found) for d in docs], "llm_a")
    b = _run(
        [
            Prediction(doc_id="d0", lane_id="llm_b", spans=found),
            Prediction(doc_id="d1", lane_id="llm_b", spans=(), failure="truncated"),
        ],
        "llm_b",
    )
    result = answered_by_both(score_lane_run(a, docs)[0], score_lane_run(b, docs)[0])
    assert result.docs == 1 and result.a.f2 == result.b.f2 == 1.0


def test_checks_render_as_two_tables() -> None:
    doc = _doc()
    run = _run([_scored(doc, {"Ann": 0.9})])
    page = analyses_markdown(
        [("decision_words:jev", "tab", context_position(run, [doc]))],
        [],
    )
    assert sum(line.startswith("|---") for line in page.splitlines()) == 2
    assert "| decision_words:jev | tab | 7 |" in page
