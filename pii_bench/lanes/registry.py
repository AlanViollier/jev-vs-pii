"""Build a lane from its id: `regex`, `jev_words`, `llm_sayback:qwen3-30b`, ..."""

from __future__ import annotations

from dataclasses import dataclass

from pii_bench.clients import ChatClient, DecisionsClient
from pii_bench.config import AppSettings
from pii_bench.decode import DecodeParams
from pii_bench.exceptions import ConfigError
from pii_bench.lanes.base import Lane
from pii_bench.lanes.jev import JevLane
from pii_bench.lanes.jev_designs import DESIGNS
from pii_bench.lanes.llm import LlmLane
from pii_bench.lanes.llm_formats import FORMATS
from pii_bench.lanes.mask_all import MaskAllLane
from pii_bench.lanes.regex import RegexLane


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
    *(f"jev_{name}" for name in DESIGNS),
    *(f"llm_{name}" for name in FORMATS),
)


def build_lane(lane_id: str, deps: LaneDeps, decoder: DecodeParams | None = None) -> Lane:
    """Parse `lane_id` (`name` or `name:model`) and construct the lane.

    Parameters
    ----------
    lane_id:
        A name from `LANE_IDS`; LLM lanes add `:<model key>` from `settings.models`.
    deps:
        Shared clients and settings.
    decoder:
        Span decoder for Jev lanes; threshold 0.5 when omitted.

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
    if model_key:
        raise ConfigError(f"{lane_id}: only llm_* lanes take a model")
    if name.startswith("jev_") and name.removeprefix("jev_") in DESIGNS:
        return JevLane(deps.decisions, DESIGNS[name.removeprefix("jev_")], decoder)
    match name:
        case "mask_all":
            return MaskAllLane()
        case "regex":
            return RegexLane()
        ## Local-model lanes import here, so only they need the heavy optional NER extra.
        case "presidio":
            from pii_bench.lanes.presidio import PresidioLane

            return PresidioLane()
        case "privacy_filter":
            from pii_bench.lanes.privacy_filter import PrivacyFilterLane

            return PrivacyFilterLane()
        case "gliner_pii":
            from pii_bench.lanes.gliner_pii import GlinerPiiLane

            return GlinerPiiLane()
    raise ConfigError(f"unknown lane {lane_id!r}; known: {', '.join(LANE_IDS)}")
