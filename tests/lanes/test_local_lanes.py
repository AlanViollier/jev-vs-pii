"""Local-model lanes: the pure parts always, the models themselves when the NER extra is installed."""

from __future__ import annotations

import asyncio
import importlib.util

import pytest

from jev_vs_pii.lanes.gliner_pii import windows
from jev_vs_pii.lanes.privacy_filter import bioes_spans
from jev_vs_pii.schema import Doc, Span
from jev_vs_pii.words import split_words, word_scores_from

_TEXT = "Mail Marie Dupont at marie@example.fr today."


def test_bioes_tags_merge_into_labelled_spans() -> None:
    tokens = [
        (0, 4, "O", 0.01),
        (4, 10, "B-private_person", 0.9),
        (10, 17, "E-private_person", 0.7),
        (20, 37, "S-private_email", 0.99),
        (37, 44, "O", 0.02),
    ]
    spans = bioes_spans(_TEXT, tokens)
    assert [(_TEXT[s.start : s.end], s.label) for s in spans] == [
        ("Marie Dupont", "PERSON"),
        ("marie@example.fr", "CONTACT"),
    ]
    assert spans[0].score == pytest.approx(0.8)


def test_stray_tags_still_make_spans() -> None:
    tokens = [(5, 10, "I-private_person", 0.8), (10, 17, "E-private_date", 0.6)]
    assert [s.label for s in bioes_spans(_TEXT, tokens)] == ["PERSON", "DATETIME"]


@pytest.mark.parametrize(
    ("n_words", "expected"),
    [
        (0, []),
        (30, [(0, 30)]),
        (250, [(0, 250)]),
        (260, [(0, 250), (200, 260)]),
        (600, [(0, 250), (200, 450), (400, 600)]),
    ],
)
def test_windows_cover_every_word_with_overlap(
    n_words: int, expected: list[tuple[int, int]]
) -> None:
    assert windows(n_words, size=250, overlap=50) == expected


def test_word_scores_take_the_best_range_touching_each_word() -> None:
    words = split_words(_TEXT)
    scores = word_scores_from(
        words, [Span(start=5, end=17, score=0.4), Span(start=11, end=17, score=0.9)]
    )
    assert [round(s.p_pii, 2) for s in scores] == [0.0, 0.4, 0.9, 0.0, 0.0, 0.0]


@pytest.mark.skipif(
    importlib.util.find_spec("transformers") is None, reason="needs the optional NER extra"
)
@pytest.mark.parametrize("lane_id", ["privacy_filter", "gliner_pii"])
def test_local_models_find_a_name_and_an_email(lane_id: str) -> None:
    from jev_vs_pii.lanes.gliner_pii import GlinerPiiLane
    from jev_vs_pii.lanes.privacy_filter import PrivacyFilterLane

    lane = PrivacyFilterLane() if lane_id == "privacy_filter" else GlinerPiiLane()
    doc = Doc(id="d", dataset="ai4privacy", split="test", text=_TEXT, gold=())
    prediction = asyncio.run(lane.predict(doc))
    found = [_TEXT[s.start : s.end] for s in prediction.spans]
    ## Privacy Filter's own decoder ends the email one word late ("... today"); so does opf.
    assert "Marie Dupont" in found
    assert any(text.startswith("marie@example.fr") for text in found)
    assert prediction.word_scores is not None and len(prediction.word_scores) == 6
