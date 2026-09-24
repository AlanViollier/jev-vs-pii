"""Runs on disk: runs/<run_id>/<lane>__<dataset>__<split>.json."""

from __future__ import annotations

from pathlib import Path

from pii_bench.schema import LaneRun


def new_run_dir(runs_dir: Path) -> Path:
    """Create `runs_dir/<timestamp>` and return it."""
    raise NotImplementedError


def save_lane_run(run_dir: Path, lane_run: LaneRun) -> Path:
    """Write one lane run as JSON; returns the file path."""
    raise NotImplementedError


def load_lane_runs(run_dir: Path) -> list[LaneRun]:
    """Read every lane run in `run_dir`."""
    raise NotImplementedError
