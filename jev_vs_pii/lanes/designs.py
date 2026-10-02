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
_NONE = {"NONE": "not personal information"}
## Synthetic text is full of "Account number: 4417…"; without this option the field name reads as an ID.
_FIELD_NAME = {
    "FIELD_NAME": "the name of a kind of information, like 'email' or 'account number', not the information itself"
}
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


def _typed(name: str, not_pii: Mapping[str, str]) -> Design:
    """One choice per word, a PII type or one of `not_pii`; the word scores 1 minus the `not_pii` probabilities."""
    criteria = {**not_pii, **_TYPE_OPTIONS}

    def ask(doc: Doc, words: Sequence[Word], i: int) -> dict[str, Question]:
        return {
            f"t{i}": Choice(
                instructions=f'In "{in_context(doc.text, words, i)}", what is the bracketed word?',
                criteria=dict(criteria),
            )
        }

    def score(answers: Mapping[str, Answer], _words: Sequence[Word], i: int) -> WordScore:
        answer = answers[f"t{i}"]
        if not isinstance(answer, ChoiceAnswer):
            raise ProviderError(f"t{i}: expected a choice answer, got {answer.type}")
        probs = {label: answer.probabilities.get(label, 0.0) for label in criteria}
        p_pii = min(max(1.0 - sum(probs.pop(label) for label in not_pii), 0.0), 1.0)
        return WordScore(p_pii=p_pii, label_probs=probs)

    return Design(name=name, ask=ask, score=score)


## Stop words that can be PII: a month, a time of day, a country, a US state.
_STOP_WORDS_ALWAYS_ASKED = frozenset({"may", "am", "us", "ca"})


@cache
def _stop_words() -> frozenset[str]:
    from spacy.lang.en.lex_attrs import like_num  # the ner extra
    from spacy.lang.en.stop_words import STOP_WORDS

    ## Number words ("three years", "forty") can be part of a date, a duration or an age.
    numbers = {w for w in STOP_WORDS if like_num(w)}  # type: ignore[no-untyped-call]  # spaCy ships no types
    return frozenset(STOP_WORDS) - numbers - _STOP_WORDS_ALWAYS_ASKED


def skipping_stop_words(design: Design) -> Design:
    """`design`, except spaCy's English stop words are never asked about and score 0.

    Number words and the stop words in `_STOP_WORDS_ALWAYS_ASKED` are still asked.
    """

    def ask(doc: Doc, words: Sequence[Word], i: int) -> dict[str, Question]:
        return {} if words[i].text.lower() in _stop_words() else design.ask(doc, words, i)

    def score(answers: Mapping[str, Answer], words: Sequence[Word], i: int) -> WordScore:
        if words[i].text.lower() in _stop_words():
            return WordScore(p_pii=0.0)
        return design.score(answers, words, i)

    return Design(name=f"{design.name}_skip", ask=ask, score=score)


WORDS = Design(name="words", ask=_ask_is_pii, score=_score_is_pii)
BIO = Design(name="bio", ask=_ask_continues, score=_score_continues)
TYPED = _typed("typed", _NONE)
TYPED_SKIP = skipping_stop_words(TYPED)
FIELDS = _typed("fields", {**_NONE, **_FIELD_NAME})
FIELDS_SKIP = skipping_stop_words(FIELDS)

DESIGNS: dict[str, Design] = {
    d.name: d for d in (WORDS, BIO, TYPED, TYPED_SKIP, FIELDS, FIELDS_SKIP)
}
