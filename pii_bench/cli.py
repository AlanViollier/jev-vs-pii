"""`pii-bench` command line: fetch · run · tune · score · report."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from pii_bench.config import get_settings
from pii_bench.data import fetch_ai4privacy, fetch_tab
from pii_bench.schema import Dataset, Split, Tier

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def fetch() -> None:
    """Download both datasets and TAB's evaluation script into the data dir."""
    data_dir = get_settings().data_dir
    for fetched in (fetch_ai4privacy(data_dir), fetch_tab(data_dir)):
        typer.echo(f"ok  {fetched}")


@app.command()
def run(
    lanes: Annotated[
        str, typer.Option(help="Comma-separated lane ids, e.g. jev_words,llm_offsets:qwen3-8b")
    ],
    dataset: Annotated[Dataset, typer.Option()],
    split: Annotated[Split, typer.Option()] = "test",
    tier: Annotated[Tier, typer.Option()] = "smoke",
    replay: Annotated[
        bool, typer.Option(help="Serve cached responses at their recorded latency")
    ] = False,
) -> None:
    """Run lanes on a dataset split with the live dashboard; stops at the budget cap."""
    raise NotImplementedError


@app.command()
def tune(
    lanes: Annotated[str, typer.Option(help="Per-word lanes to tune")],
    dataset: Annotated[Dataset, typer.Option()],
) -> None:
    """Grid-search decoder settings on the dev split and save the winners."""
    raise NotImplementedError


@app.command()
def score(run_dir: Annotated[Path, typer.Argument()]) -> None:
    """Score every lane run in `run_dir`; write scores.json and results.md."""
    raise NotImplementedError


@app.command()
def report(run_dir: Annotated[Path, typer.Argument()]) -> None:
    """Build the HTML report for a scored run."""
    raise NotImplementedError
