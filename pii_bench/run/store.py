"""Runs on disk: runs/<run>/<lane>__<dataset>__<split>.json, one file per lane run."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pii_bench.schema import LaneRun


def new_run_dir(runs_dir: Path) -> Path:
    """Create `runs_dir/<local timestamp>` and return it."""
    run_dir = runs_dir / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_dir.mkdir(parents=True)
    return run_dir


def save_lane_run(run_dir: Path, lane_run: LaneRun) -> Path:
    """Write one lane run as JSON, replacing an earlier run of the same lane on the same split."""
    ## `:` separates an LLM lane from its model and isn't allowed in every filesystem.
    lane = lane_run.lane.id.replace(":", "@")
    path = run_dir / f"{lane}__{lane_run.dataset}__{lane_run.split}.json"
    path.write_text(lane_run.model_dump_json())
    return path


def load_lane_runs(run_dir: Path) -> list[LaneRun]:
    """Read every lane run in `run_dir`, in file-name order."""
    return [
        LaneRun.model_validate_json(path.read_text()) for path in sorted(run_dir.glob("*__*.json"))
    ]
