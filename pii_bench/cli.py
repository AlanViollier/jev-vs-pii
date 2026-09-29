"""`pii-bench` command line: fetch · run · tune · score · report."""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn

from pii_bench.clients import ChatClient, DecisionsClient, Ledger, ResponseCache
from pii_bench.config import AppSettings, get_settings
from pii_bench.data import fetch_ai4privacy, fetch_nemotron, fetch_tab, load_docs
from pii_bench.decode import describe
from pii_bench.exceptions import BudgetExceeded, PiiBenchError
from pii_bench.lanes import Lane, LaneDeps, build_lane
from pii_bench.metrics.results import human_lane_run, score_lane_run
from pii_bench.report.markdown import results_markdown
from pii_bench.report.svg import pareto_svg
from pii_bench.run import (
    load_lane_runs,
    load_tuned,
    new_run_dir,
    ranked,
    run_lane,
    save_lane_run,
    save_tuned,
    select_docs,
    tune_lane_run,
)
from pii_bench.schema import Dataset, Doc, LaneRun, ResultRow, Split, Tier

app = typer.Typer(no_args_is_help=True, add_completion=False)
_console = Console()
_DECODERS_FILE = "decoders.json"


@app.command()
def fetch() -> None:
    """Download the three datasets and TAB's evaluation script into the data dir."""
    data_dir = get_settings().data_dir
    for fetched in (fetch_ai4privacy(data_dir), fetch_tab(data_dir), fetch_nemotron(data_dir)):
        typer.echo(f"ok  {fetched}")


@app.command()
def run(
    lanes: Annotated[
        str,
        typer.Option(help="Comma-separated lane ids, e.g. regex,jev_words,llm_sayback:qwen3-30b"),
    ],
    dataset: Annotated[Dataset, typer.Option()],
    split: Annotated[Split, typer.Option()] = "test",
    tier: Annotated[Tier, typer.Option()] = "smoke",
    out: Annotated[
        Path | None, typer.Option(help="Add to this run folder instead of starting a new one")
    ] = None,
    replay: Annotated[
        bool, typer.Option(help="Serve cached responses at their recorded latency")
    ] = False,
) -> None:
    """Run lanes on a dataset split; stops before any call that would pass the budget cap."""
    settings = get_settings()
    ledger = Ledger(settings.cache_dir / "ledger.json", settings.budget_cap_usd)
    deps = _deps(settings, ledger, ResponseCache(settings.cache_dir / "responses", replay=replay))
    built = [build_lane(lane_id.strip(), deps) for lane_id in lanes.split(",")]
    docs = select_docs(load_docs(settings.data_dir, dataset, split, settings.seed), tier)
    run_dir = out or new_run_dir(settings.runs_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(_run_lanes(built, docs, dataset, split, tier, run_dir, settings, ledger))
    except BudgetExceeded as error:
        _console.print(f"[bold red]stopped:[/] {error}")
        raise typer.Exit(1) from error
    _console.print(f"→ {run_dir} · spent ${ledger.spent_usd:.4f} of ${settings.budget_cap_usd}")


@app.command()
def tune(run_dir: Annotated[Path, typer.Argument(help="A run on the dev split")]) -> None:
    """Grid-search every decoder on the dev run's word scores; save the best of each kind."""
    settings = get_settings()
    path = settings.runs_dir / _DECODERS_FILE
    tuned = load_tuned(path)
    for lane_run, docs in _with_docs(load_lane_runs(run_dir), settings):
        if lane_run.split != "dev" or not lane_run.predictions[0].word_scores:
            continue
        decoders = ranked(tune_lane_run(lane_run, docs))
        tuned.setdefault(lane_run.lane.id, {})[lane_run.dataset] = decoders
        for decoder in decoders:
            _console.print(
                f"{lane_run.lane.id:<14} {lane_run.dataset:<10} "
                f"dev F2 {decoder.dev_f2:.3f}  {describe(decoder.params)}"
            )
    save_tuned(path, tuned)
    _console.print(f"→ {path}")


@app.command()
def score(run_dir: Annotated[Path, typer.Argument()]) -> None:
    """Score every lane run in `run_dir` (plus tuned decoders); write scores.json and results.md."""
    settings = get_settings()
    tuned = load_tuned(settings.runs_dir / _DECODERS_FILE)
    rows: list[ResultRow] = []
    ## The human row is scored on the docs the lanes ran on, so smoke and pilot compare like for like.
    ran: dict[tuple[Dataset, Split], set[str]] = defaultdict(set)
    split_docs: dict[tuple[Dataset, Split], list[Doc]] = {}
    for lane_run, docs in _with_docs(load_lane_runs(run_dir), settings):
        decoders = tuned.get(lane_run.lane.id, {}).get(lane_run.dataset, [])
        rows += score_lane_run(lane_run, docs, seed=settings.seed, headline=not decoders)
        for rank, decoder in enumerate(decoders):
            rows += score_lane_run(
                lane_run, docs, decoder.params, seed=settings.seed, headline=rank == 0
            )
        key = (lane_run.dataset, lane_run.split)
        ran[key] |= {prediction.doc_id for prediction in lane_run.predictions}
        split_docs[key] = docs
    for key, doc_ids in ran.items():
        human = human_lane_run([doc for doc in split_docs[key] if doc.id in doc_ids])
        if human is not None:
            rows += score_lane_run(human, split_docs[key], seed=settings.seed)
    (run_dir / "scores.json").write_text(
        json.dumps([row.model_dump(mode="json") for row in rows], indent=1)
    )
    report = results_markdown(rows, seed=settings.seed)
    (run_dir / "results.md").write_text(report)
    typer.echo(report)


@app.command()
def report(run_dir: Annotated[Path, typer.Argument()]) -> None:
    """Draw the README chart from a scored run: headline F2 vs $/1k docs, one panel per dataset."""
    rows = [
        ResultRow.model_validate(row) for row in json.loads((run_dir / "scores.json").read_text())
    ]
    panels = []
    for dataset in ("ai4privacy", "tab"):
        chosen = [r for r in rows if r.dataset == dataset and r.mode == "word" and r.headline]
        if chosen:
            panels.append((f"{dataset} · {chosen[0].split} · word-level F2", chosen))
    path = run_dir / "pareto.svg"
    path.write_text(pareto_svg(panels))
    _console.print(f"→ {path}")


def _deps(settings: AppSettings, ledger: Ledger, cache: ResponseCache) -> LaneDeps:
    key = settings.openrouter_api_key.get_secret_value()
    return LaneDeps(
        settings=settings,
        decisions=DecisionsClient(key, settings.jev_model, ledger, cache),
        chat=ChatClient(key, ledger, cache),
    )


async def _run_lanes(
    lanes: Sequence[Lane],
    docs: Sequence[Doc],
    dataset: Dataset,
    split: Split,
    tier: Tier,
    run_dir: Path,
    settings: AppSettings,
    ledger: Ledger,
) -> None:
    """One event loop for every lane, so the HTTP clients keep their connections."""
    columns = (
        TextColumn("{task.description:<24}"),
        BarColumn(complete_style="#C2410C"),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )
    for lane in lanes:
        spent_before: Decimal = ledger.spent_usd
        started_at, started = datetime.now(), time.perf_counter()
        with Progress(*columns, console=_console) as progress:
            task = progress.add_task(lane.info.id, total=len(docs))
            predictions = await run_lane(
                lane, docs, settings.concurrency, lambda *_, task=task: progress.advance(task)
            )
        lane_run = LaneRun(
            run_id=run_dir.name,
            lane=lane.info,
            dataset=dataset,
            split=split,
            tier=tier,
            started_at=started_at,
            wall_clock_s=time.perf_counter() - started,
            predictions=tuple(predictions),
        )
        save_lane_run(run_dir, lane_run)
        failed = sum(p.failed for p in predictions)
        _console.print(
            f"  {len(predictions)} docs · {failed} failed · "
            f"${ledger.spent_usd - spent_before:.4f} new spend"
        )


def _with_docs(
    lane_runs: Sequence[LaneRun], settings: AppSettings
) -> list[tuple[LaneRun, list[Doc]]]:
    """Pair each run with its split's gold docs, loading each split once."""
    loaded: dict[tuple[Dataset, Split], list[Doc]] = {}
    paired = []
    for lane_run in lane_runs:
        key = (lane_run.dataset, lane_run.split)
        if key not in loaded:
            loaded[key] = load_docs(settings.data_dir, *key, settings.seed)
        paired.append((lane_run, loaded[key]))
    return paired


def main() -> None:
    """Entry point that turns expected failures into one clean line."""
    try:
        app()
    except PiiBenchError as error:
        _console.print(f"[bold red]error:[/] {error}")
        raise SystemExit(1) from error
