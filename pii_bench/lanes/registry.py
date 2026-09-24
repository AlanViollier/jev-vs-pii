"""Build a lane from its id: `jev_words`, `presidio`, `llm_offsets:qwen3-8b`, ..."""

from __future__ import annotations

from dataclasses import dataclass

from pii_bench.clients import ChatClient, DecisionsClient, LocalClient
from pii_bench.config import AppSettings
from pii_bench.lanes.base import Lane


@dataclass(frozen=True)
class LaneDeps:
    """Clients a lane may need. Built once per run and shared."""

    settings: AppSettings
    decisions: DecisionsClient
    chat: ChatClient
    local: LocalClient


LANE_IDS = (
    "regex",
    "presidio",
    "gliner",
    "jev_words",
    "jev_tree",
    "jev_chunks",
    "jev_bio",
    "jev_typed",
    "llm_offsets",
    "llm_sayback",
    "llm_tagged",
    "cascade",
)


def build_lane(lane_id: str, deps: LaneDeps) -> Lane:
    """Parse `lane_id` (`name` or `name:model`) and construct the lane.

    Parameters
    ----------
    lane_id:
        A name from `LANE_IDS`, with `:model` for LLM and cascade lanes;
        the model key must exist in `settings.models`.
    deps:
        Shared clients and settings.

    Returns
    -------
    Lane
        Raises `ConfigError` for an unknown name or model.
    """
    raise NotImplementedError
