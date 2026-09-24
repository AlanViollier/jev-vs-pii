"""One self-contained HTML page: Pareto curve, reliability diagram, TAB doc diff viewer."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pii_bench.metrics.calibration import ReliabilityBin
from pii_bench.schema import Doc, Prediction, ResultRow


def render_report(
    rows: Sequence[ResultRow],
    reliability: dict[str, list[ReliabilityBin]],
    viewer_docs: Sequence[tuple[Doc, dict[str, Prediction]]],
    out_path: Path,
) -> Path:
    """Write the report page with Chart.js inlined, in ember style.

    Parameters
    ----------
    rows:
        Results to plot as F2 vs $/1k docs.
    reliability:
        Lane id → reliability bins, for lanes that have confidences.
    viewer_docs:
        TAB docs only (ai4privacy text must never appear in public output), each with
        the predictions of the lanes to compare.
    out_path:
        Where to write the HTML.

    Returns
    -------
    Path
        `out_path`.
    """
    raise NotImplementedError
