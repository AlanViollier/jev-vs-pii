"""Results as Markdown tables for the README and run folders."""

from __future__ import annotations

from collections.abc import Sequence

from pii_bench.schema import ResultRow


def results_table(rows: Sequence[ResultRow]) -> str:
    """Render one row per lane: F2 with CI, P, R, ECE, $/1k docs, latency, can-run-on-EU-data.

    Parameters
    ----------
    rows:
        Scored lane runs for one dataset split and match mode.

    Returns
    -------
    str
        A Markdown table, rows sorted by F2.
    """
    raise NotImplementedError
