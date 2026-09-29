"""A generative model finding PII in one call, in one of the answer formats. Lane ids: `llm_<format>:<model>`."""

from __future__ import annotations

from pydantic import ValidationError

from pii_bench.clients import ChatClient, Message
from pii_bench.config import ModelSpec
from pii_bench.exceptions import AlignmentError
from pii_bench.lanes.llm_formats import AnswerFormat
from pii_bench.schema import Doc, LaneInfo, Prediction
from pii_bench.taxonomy import definition


class LlmLane:
    """Lane `llm_<format>:<model_key>`: the PII definition and format rules as system prompt, the doc as user turn."""

    def __init__(
        self, client: ChatClient, answer_format: AnswerFormat, model_key: str, model: ModelSpec
    ) -> None:
        self.info = LaneInfo(
            id=f"llm_{answer_format.name}:{model_key}", family="llm", model=model.id
        )
        self._client = client
        self._format = answer_format
        self._model = model

    async def predict(self, doc: Doc) -> Prediction:
        """Ask the model once; an answer that is cut off or won't parse counts as finding nothing."""
        system = (
            "You find personal information in text.\n\n"
            f"{definition(doc)}\n\n{self._format.instructions}"
        )
        result = await self._client.complete(
            self._model,
            [Message(role="system", content=system), Message(role="user", content=doc.text)],
            self._format.json_schema,
        )
        base = Prediction(
            doc_id=doc.id,
            lane_id=self.info.id,
            spans=(),
            usage=result.usage,
            answer=result.text,
            provider=result.provider,
        )
        if result.truncated:
            return base.model_copy(update={"failed": True, "failure": "truncated"})
        try:
            spans, dropped = self._format.parse(doc.text, result.text)
        except ValidationError:
            return base.model_copy(update={"failed": True, "failure": "unparseable"})
        except AlignmentError:
            return base.model_copy(update={"failed": True, "failure": "misaligned"})
        return base.model_copy(update={"spans": tuple(spans), "dropped": dropped})
