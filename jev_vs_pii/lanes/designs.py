"""Question designs for decision models: what to ask about each word, and the word score read back from the answers.

The PII definition sits in the state; questions point at one word in its context.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache

from jev_vs_pii.clients import Choice, Noul
from jev_vs_pii.clients.decisions import ChoiceAnswer, NoulAnswer
from jev_vs_pii.exceptions import ProviderError
from jev_vs_pii.schema import Doc, Word, WordScore

## Words either side of the asked word, so repeats of the same word stay distinguishable.
_CONTEXT_BEFORE = 3
_CONTEXT_AFTER = 2
_NONE = "NONE"
## Short option texts: the full definitions are already in the state.
_TYPE_OPTIONS = {
    "PERSON": "a name or title",
    "LOCATION": "a place tied to a person",
    "CONTACT": "email, phone, handle or IP",
    "ID": "an identifying number or secret",
    "DATETIME": "a date or time tied to a person",
    "OTHER": "another identifying detail",
}

Question = Noul | Choice
Answer = NoulAnswer | ChoiceAnswer
AskWord = Callable[[Doc, Sequence[Word], int], dict[str, Question]]
ScoreWord = Callable[[Mapping[str, Answer], Sequence[Word], int], WordScore]


@dataclass(frozen=True)
class Design:
    """Questions for word i (keys must embed i), and the word score read back from their answers."""

    name: str
    ask: AskWord
    score: ScoreWord


def in_context(text: str, words: Sequence[Word], i: int) -> str:
    """The word in brackets with a few neighbours, as written: `to Marie [Dupont] at 12`."""
    left = words[max(i - _CONTEXT_BEFORE, 0)].start
    right = words[min(i + _CONTEXT_AFTER, len(words) - 1)].end
    word = words[i]
    snippet = f"{text[left : word.start]}[{word.text}]{text[word.end : right]}"
    return " ".join(snippet.split())


def _ask_is_pii(doc: Doc, words: Sequence[Word], i: int) -> dict[str, Question]:
    return {
        f"p{i}": Noul(
            instructions=f'In "{in_context(doc.text, words, i)}", is the bracketed word personal information?'
        )
    }


def _ask_continues(doc: Doc, words: Sequence[Word], i: int) -> dict[str, Question]:
    questions = _ask_is_pii(doc, words, i)
    if i > 0:
        questions[f"c{i}"] = Noul(
            instructions=(
                f'In "{in_context(doc.text, words, i)}", is the bracketed word part of the same '
                "piece of information as the word right before it?"
            )
        )
    return questions


def _ask_type(doc: Doc, words: Sequence[Word], i: int) -> dict[str, Question]:
    return {
        f"t{i}": Choice(
            instructions=f'In "{in_context(doc.text, words, i)}", what is the bracketed word?',
            criteria={_NONE: "not personal information", **_TYPE_OPTIONS},
        )
    }


def _noul(answers: Mapping[str, Answer], key: str) -> float:
    answer = answers[key]
    if not isinstance(answer, NoulAnswer):
        raise ProviderError(f"{key}: expected a yes/no answer, got {answer.type}")
    return answer.noul


def _score_is_pii(answers: Mapping[str, Answer], _words: Sequence[Word], i: int) -> WordScore:
    return WordScore(p_pii=_noul(answers, f"p{i}"))


def _score_continues(answers: Mapping[str, Answer], _words: Sequence[Word], i: int) -> WordScore:
    p_continue = _noul(answers, f"c{i}") if i > 0 else None
    return WordScore(p_pii=_noul(answers, f"p{i}"), p_continue=p_continue)


def _score_type(answers: Mapping[str, Answer], _words: Sequence[Word], i: int) -> WordScore:
    answer = answers[f"t{i}"]
    if not isinstance(answer, ChoiceAnswer):
        raise ProviderError(f"t{i}: expected a choice answer, got {answer.type}")
    probs = {label: answer.probabilities.get(label, 0.0) for label in [_NONE, *_TYPE_OPTIONS]}
    p_pii = min(max(1.0 - probs.pop(_NONE), 0.0), 1.0)
    return WordScore(p_pii=p_pii, label_probs=probs)


@cache
def _stop_words() -> frozenset[str]:
    from spacy.lang.en.stop_words import STOP_WORDS  # the ner extra

    return frozenset(STOP_WORDS)


def skipping_stop_words(design: Design) -> Design:
    """`design`, except words in spaCy's English stop-word list are never asked about and score 0."""

    def ask(doc: Doc, words: Sequence[Word], i: int) -> dict[str, Question]:
        return {} if words[i].text.lower() in _stop_words() else design.ask(doc, words, i)

    def score(answers: Mapping[str, Answer], words: Sequence[Word], i: int) -> WordScore:
        if words[i].text.lower() in _stop_words():
            return WordScore(p_pii=0.0)
        return design.score(answers, words, i)

    return Design(name=f"{design.name}_skip", ask=ask, score=score)


WORDS = Design(name="words", ask=_ask_is_pii, score=_score_is_pii)
BIO = Design(name="bio", ask=_ask_continues, score=_score_continues)
TYPED = Design(name="typed", ask=_ask_type, score=_score_type)
TYPED_SKIP = skipping_stop_words(TYPED)

DESIGNS: dict[str, Design] = {d.name: d for d in (WORDS, BIO, TYPED, TYPED_SKIP)}
