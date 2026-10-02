"""Build a lane from its id: `regex`, `decision_words:jev`, `llm_sayback:qwen3-30b`, ..."""

from __future__ import annotations

from dataclasses import dataclass

from jev_vs_pii.clients import ChatClient, DecisionsClient
from jev_vs_pii.config import AppSettings
from jev_vs_pii.decode import DecodeParams
from jev_vs_pii.exceptions import ConfigError
from jev_vs_pii.lanes.base import Lane
from jev_vs_pii.lanes.decision import DecisionLane, DecisionModel
from jev_vs_pii.lanes.designs import DESIGNS
from jev_vs_pii.lanes.jev import JevModel
from jev_vs_pii.lanes.llm import LlmLane
from jev_vs_pii.lanes.llm_formats import FORMATS
from jev_vs_pii.lanes.mask_all import MaskAllLane
from jev_vs_pii.lanes.regex import RegexLane


@dataclass(frozen=True)
class LaneDeps:
    """Clients a lane may need. Built once per run and shared."""

    settings: AppSettings
    decisions: DecisionsClient
    chat: ChatClient


LANE_IDS = (
    "mask_all",
    "regex",
    "presidio",
    "privacy_filter",
    "gliner_pii",
    *(f"decision_{name}" for name in DESIGNS),
    *(f"llm_{name}" for name in FORMATS),
)


def build_lane(lane_id: str, deps: LaneDeps, decoder: DecodeParams | None = None) -> Lane:
    """Parse `lane_id` (`name` or `name:model`) and construct the lane.

    Parameters
    ----------
    lane_id:
        A name from `LANE_IDS`; LLM lanes add `:<model key>` from `settings.models`,
        decision lanes `:jev`.
    deps:
        Shared clients and settings.
    decoder:
        Span decoder for decision lanes; threshold 0.5 when omitted.

    Returns
    -------
    Lane
        Raises `ConfigError` for an unknown name or model.
    """
    name, _, model_key = lane_id.partition(":")
    if name.startswith("llm_") and name.removeprefix("llm_") in FORMATS:
        if model_key not in deps.settings.models:
            known = ", ".join(deps.settings.models) or "none configured"
            raise ConfigError(f"{lane_id}: unknown model {model_key!r} (known: {known})")
        answer_format = FORMATS[name.removeprefix("llm_")]
        return LlmLane(deps.chat, answer_format, model_key, deps.settings.models[model_key])
    if name.startswith("decision_") and name.removeprefix("decision_") in DESIGNS:
        return DecisionLane(
            _decision_model(lane_id, model_key, deps),
            DESIGNS[name.removeprefix("decision_")],
            decoder,
        )
    if model_key:
        raise ConfigError(f"{lane_id}: only llm_* and decision_* lanes take a model")
    match name:
        case "mask_all":
            return MaskAllLane()
        case "regex":
            return RegexLane()
        ## Local-model lanes import here, so only they need the heavy optional NER extra.
        case "presidio":
            from jev_vs_pii.lanes.presidio import PresidioLane

            return PresidioLane()
        case "privacy_filter":
            from jev_vs_pii.lanes.privacy_filter import PrivacyFilterLane

            return PrivacyFilterLane()
        case "gliner_pii":
            from jev_vs_pii.lanes.gliner_pii import GlinerPiiLane

            return GlinerPiiLane()
    raise ConfigError(f"unknown lane {lane_id!r}; known: {', '.join(LANE_IDS)}")


def _decision_model(lane_id: str, model_key: str, deps: LaneDeps) -> DecisionModel:
    if model_key == "jev":
        return JevModel(deps.decisions)
    raise ConfigError(f"{lane_id}: unknown decision model {model_key!r} (known: jev)")
