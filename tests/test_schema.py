"""Schema invariants: offsets must describe a non-empty range, probabilities stay in [0, 1]."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import TypeAdapter, ValidationError

from pii_bench.decode import DecodeParams, Hysteresis, Viterbi
from pii_bench.schema import Span, Usage, Word, WordScore


@pytest.mark.parametrize("model", [Span, Word])
def test_empty_or_reversed_range_is_rejected(model: type[Span] | type[Word]) -> None:
    kwargs = {"text": "x"} if model is Word else {}
    with pytest.raises(ValidationError):
        model(start=5, end=5, **kwargs)
    with pytest.raises(ValidationError):
        model(start=5, end=3, **kwargs)


def test_span_score_must_be_a_probability() -> None:
    with pytest.raises(ValidationError):
        Span(start=0, end=3, score=1.2)


def test_word_score_optional_fields_default_to_none() -> None:
    score = WordScore(p_pii=0.4)
    assert score.p_continue is None
    assert score.label_probs is None


def test_usage_cost_is_decimal() -> None:
    assert Usage(cost_usd=Decimal("0.000018396")).cost_usd == Decimal("0.000018396")


def test_decode_params_round_trip_by_kind() -> None:
    adapter: TypeAdapter[DecodeParams] = TypeAdapter(DecodeParams)
    assert adapter.validate_python({"kind": "hysteresis", "high": 0.7, "low": 0.2}) == Hysteresis(
        high=0.7, low=0.2
    )
    assert isinstance(adapter.validate_python({"kind": "viterbi"}), Viterbi)
