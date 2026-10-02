"""`jev-vs-pii` command line: fetch · run · tune · score · export."""

from __future__ import annotations

import asyncio
import json
import shutil
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

from jev_vs_pii.clients import ChatClient, DecisionsClient, Ledger, ResponseCache
from jev_vs_pii.config import AppSettings, get_settings
from jev_vs_pii.data import fetch_ai4privacy, fetch_nemotron, fetch_tab, load_docs
from jev_vs_pii.decode import DecodeParams, Threshold, describe
from jev_vs_pii.exceptions import BudgetExceeded, JevVsPiiError, ProviderError
from jev_vs_pii.lanes import Lane, LaneDeps, build_lane
from jev_vs_pii.metrics.results import human_lane_run, score_lane_run
from jev_vs_pii.report.analyses import (
    analyses_markdown,
    answered_by_both,
    context_position,
    stop_word_skip,
)
from jev_vs_pii.report.export import (
    EXAMPLE_DATASETS,
    curve_records,
    example_records,
    headline_records,
    paired_records,
    per_doc_records,
)
from jev_vs_pii.report.markdown import results_markdown
from jev_vs_pii.run import (
    headline_decoder,
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
from jev_vs_pii.run.tune import Tuned
from jev_vs_pii.schema import Dataset, Doc, LaneRun, ResultRow, Split, Tier

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
        typer.Option(
            help="Comma-separated lane ids, e.g. regex,decision_words:jev,llm_sayback:qwen3-30b"
        ),
    ],
    dataset: Annotated[Dataset, typer.Option()],
    split: Annotated[Split, typer.Option()] = "test",
    tier: Annotated[Tier, typer.Option()] = "smoke",
    out: Annotated[
        Path | None, typer.Option(help="Add to this run folder instead of starting a new one")
    ] = None,
) -> None:
    """Run lanes on a dataset split; stops before any call that would pass the budget cap."""
    settings = get_settings()
    ledger = Ledger(settings.cache_dir / "ledger.json", settings.budget_cap_usd)
    deps = _deps(settings, ledger, ResponseCache(settings.cache_dir / "responses"))
    built = [build_lane(lane_id.strip(), deps) for lane_id in lanes.split(",")]
    docs = select_docs(load_docs(settings.data_dir, dataset, split, settings.seed), tier)
    run_dir = out or new_run_dir(settings.runs_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        failures = asyncio.run(
            _run_lanes(built, docs, dataset, split, tier, run_dir, settings, ledger)
        )
    except BudgetExceeded as error:
        _console.print(f"[bold red]stopped:[/] {error}")
        raise typer.Exit(1) from error
    _console.print(f"→ {run_dir} · spent ${ledger.spent_usd:.4f} of ${settings.budget_cap_usd}")
    if failures:
        for lane_id, failure in failures:
            _console.print(f"[bold red]not saved:[/] {lane_id}: {str(failure)[:300]}")
        _console.print("Rerun the same command: finished calls come back from the cache.")
        raise typer.Exit(1)


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
    runs = _with_docs(load_lane_runs(run_dir), settings)
    for lane_run, docs in runs:
        decoders = tuned.get(lane_run.lane.id, {}).get(lane_run.dataset, [])
        chosen = headline_decoder(decoders)
        rows += score_lane_run(
            lane_run, docs, seed=settings.seed, headline=chosen is None, data_dir=settings.data_dir
        )
        for decoder in decoders:
            rows += score_lane_run(
                lane_run,
                docs,
                decoder.params,
                seed=settings.seed,
                headline=decoder is chosen,
                data_dir=settings.data_dir,
            )
        key = (lane_run.dataset, lane_run.split)
        ran[key] |= {prediction.doc_id for prediction in lane_run.predictions}
        split_docs[key] = docs
    for key, doc_ids in ran.items():
        human = human_lane_run([doc for doc in split_docs[key] if doc.id in doc_ids])
        if human is not None:
            rows += score_lane_run(
                human, split_docs[key], seed=settings.seed, data_dir=settings.data_dir
            )
    (run_dir / "scores.json").write_text(
        json.dumps([row.model_dump(mode="json") for row in rows], indent=1)
    )
    report = f"{results_markdown(rows, seed=settings.seed)}\n{_checks(runs, rows, tuned)}"
    (run_dir / "results.md").write_text(report)
    typer.echo(report)


@app.command()
def export(
    run_dir: Annotated[Path, typer.Argument(help="A scored test run")],
    out: Annotated[Path, typer.Option(help="Where results.md and data/ go")] = Path("docs"),
) -> None:
    """Copy results.md into `out` and write chart and demo data as small JSON files in `out`/data."""
    settings = get_settings()
    rows = [
        ResultRow.model_validate(row) for row in json.loads((run_dir / "scores.json").read_text())
    ]
    decoders: dict[tuple[str, Dataset], DecodeParams] = {}
    for lane_id, by_dataset in load_tuned(settings.runs_dir / _DECODERS_FILE).items():
        for dataset, tuned in by_dataset.items():
            chosen = headline_decoder(tuned)
            if chosen is not None:
                decoders[(lane_id, dataset)] = chosen.params
    docs = {d: load_docs(settings.data_dir, d, "test", settings.seed) for d in EXAMPLE_DATASETS}
    records = {
        "headline": headline_records(rows),
        "paired": paired_records(rows, settings.seed),
        "curves": curve_records(rows),
        "per_doc": per_doc_records(rows),
        "examples": example_records(load_lane_runs(run_dir), docs, decoders),
    }
    (out / "data").mkdir(parents=True, exist_ok=True)
    for name, content in records.items():
        ## The two per-doc files are big: compact; the rest stays readable.
        indent = None if name in ("per_doc", "examples") else 1
        (out / "data" / f"{name}.json").write_text(json.dumps(content, indent=indent) + "\n")
    shutil.copyfile(run_dir / "results.md", out / "results.md")
    _console.print(f"→ {out}/results.md · {out}/data/ ({', '.join(records)})")


## Thinking off vs on, compared on the docs both answered: a cut-off answer isn't a wrong one.
_ANSWERED_PAIRS = [("llm_sayback:deepseek-v4-flash", "llm_sayback:deepseek-v4-flash-think")]


def _checks(
    runs: Sequence[tuple[LaneRun, list[Doc]]], rows: Sequence[ResultRow], tuned: Tuned
) -> str:
    """The what-ifs and checks results.md ends with, on the stored runs; no calls made."""
    ## spaCy comes with the NER extra, which TAB's official scoring already needs.
    from spacy.lang.en.stop_words import STOP_WORDS

    skips, positions = [], []
    for lane_run, docs in runs:
        if not lane_run.lane.id.endswith(":jev"):
            continue
        chosen = headline_decoder(tuned.get(lane_run.lane.id, {}).get(lane_run.dataset, []))
        decoder = chosen.params if chosen is not None else Threshold()
        key = (lane_run.lane.id, lane_run.dataset)
        skips.append((*key, stop_word_skip(lane_run, docs, decoder, STOP_WORDS)))
        positions.append((*key, context_position(lane_run, docs)))
    headline = {(r.lane.id, r.dataset): r for r in rows if r.headline and r.mode == "word"}
    answered = [
        (dataset, a, b, answered_by_both(headline[(a, dataset)], headline[(b, dataset)]))
        for a, b in _ANSWERED_PAIRS
        for dataset in sorted({dataset for _, dataset in headline})
        if (a, dataset) in headline and (b, dataset) in headline
    ]
    return analyses_markdown(skips, positions, answered)


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
) -> list[tuple[str, ProviderError]]:
    """Run every lane in one event loop, so the HTTP clients keep their connections.

    A lane whose provider keeps failing is skipped, not the whole run: the other lanes
    finish and are saved, and the failed ones are returned for the caller to report.
    """
    columns = (
        TextColumn("{task.description:<24}"),
        BarColumn(complete_style="#C2410C"),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    )
    failures: list[tuple[str, ProviderError]] = []
    for lane in lanes:
        spent_before: Decimal = ledger.spent_usd
        started_at, started = datetime.now(), time.perf_counter()
        try:
            with Progress(*columns, console=_console) as progress:
                task = progress.add_task(lane.info.id, total=len(docs))
                predictions = await run_lane(
                    lane, docs, settings.concurrency, lambda *_, task=task: progress.advance(task)
                )
        except ProviderError as error:
            failures.append((lane.info.id, error))
            continue
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
    return failures


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
    except JevVsPiiError as error:
        _console.print(f"[bold red]error:[/] {error}")
        raise SystemExit(1) from error
