"""Jev through OpenRouter's Decisions API: one text, many typed questions, probabilities back."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from pii_bench.clients.budget import Ledger
from pii_bench.clients.cache import ResponseCache
from pii_bench.schema import Usage

DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"


class Noul(BaseModel):
    """Yes/no question; the answer is the probability of yes."""

    type: Literal["noul"] = "noul"
    instructions: str


class Choice(BaseModel):
    """Pick-one question; `criteria` maps each option to its description."""

    type: Literal["choice"] = "choice"
    instructions: str
    criteria: dict[str, str]


class NoulAnswer(BaseModel):
    """Probability that the answer is yes."""

    type: Literal["noul"]
    noul: float


class ChoiceAnswer(BaseModel):
    """Picked option, the full distribution, and the model's confidence."""

    type: Literal["choice"]
    choice: str
    probabilities: dict[str, float]
    confidence: float


class DecisionResult(BaseModel):
    """Answers keyed like the questions, plus what the call cost."""

    answers: dict[str, NoulAnswer | ChoiceAnswer]
    usage: Usage


class DecisionsClient:
    """Async client for the Decisions API; every call is budget-checked and cached."""

    def __init__(self, api_key: str, model: str, ledger: Ledger, cache: ResponseCache) -> None:
        raise NotImplementedError

    async def ask(self, state: str, questions: dict[str, Noul | Choice]) -> DecisionResult:
        """Ask every question about `state` in one call.

        Parameters
        ----------
        state:
            The text the questions are about.
        questions:
            Question key → question. Keys come back unchanged in `answers`.

        Returns
        -------
        DecisionResult
            Raises `BudgetExceeded` before the call if it could pass the cap,
            `ProviderError` if the API errors or the answer doesn't parse.
        """
        raise NotImplementedError
