"""TAB's own evaluation script on our predictions, so TAB numbers compare with its paper.

The script is downloaded with the dataset (pinned commit) and never committed; it is
imported in-process and fed the spans each lane masked.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from types import ModuleType

from pii_bench.data.fetch import TAB_EVAL_SCRIPT, TAB_FILES
from pii_bench.schema import Prediction, Split

## The measures TAB's `evaluate()` returns as plain numbers (its per-type dict is skipped).
MEASURES = (
    "recall_direct_entities",
    "recall_quasi_entities",
    "token_recall",
    "mention_recall",
    "token_precision",
    "mention_precision",
    "token_f1",
)


def tab_official_scores(
    predictions: Sequence[Prediction], data_dir: Path, split: Split
) -> dict[str, float]:
    """Run TAB's `evaluate()` on one lane's TAB predictions.

    Parameters
    ----------
    predictions:
        One lane's predictions on a TAB split; only their docs are evaluated.
    data_dir:
        Root data directory holding the fetched TAB files and script.
    split:
        `dev` or `test`.

    Returns
    -------
    dict[str, float]
        The script's entity-level recall on direct and quasi identifiers, token and
        mention recall and precision, and token F1, rounded to 3 places as it prints them.
    """
    script, corpus = _gold_corpus(data_dir, split)
    masked = [
        script.MaskedDocument(p.doc_id, [(span.start, span.end) for span in p.spans])
        for p in predictions
    ]
    measures = script.evaluate(corpus, masked)
    return {name: float(measures[name]) for name in MEASURES}


@cache
def _gold_corpus(data_dir: Path, split: Split) -> tuple[ModuleType, object]:
    """Import the script and parse the gold split once per process (it runs spaCy on every doc)."""
    spec = importlib.util.spec_from_file_location(
        "tab_evaluation", data_dir / "tab" / TAB_EVAL_SCRIPT
    )
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"TAB evaluation script missing under {data_dir / 'tab'}")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    return script, script.GoldCorpus(str(data_dir / "tab" / TAB_FILES[split]))
