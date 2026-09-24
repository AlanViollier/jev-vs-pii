"""LLM returns JSON spans with character offsets. Model is a parameter: local or Haiku."""

from __future__ import annotations

from pii_bench.config import ModelSpec
from pii_bench.lanes.base import Completer
from pii_bench.schema import Doc, LaneInfo, Prediction


class LlmOffsetsLane:
    """Lane `llm_offsets:<model>`."""

    info: LaneInfo

    def __init__(self, client: Completer, model: ModelSpec, model_key: str) -> None:
        raise NotImplementedError

    async def predict(self, doc: Doc) -> Prediction:
        """Find PII in `doc`."""
        raise NotImplementedError
