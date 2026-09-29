"""Download the datasets into the local data dir. Nothing downloaded here is ever committed."""

from __future__ import annotations

from pathlib import Path

import httpx
from huggingface_hub import hf_hub_download

from pii_bench.schema import Split

## Pinned revisions: the benchmark must read the same bytes on every clone.
_AI4PRIVACY_REPO = "ai4privacy/pii-masking-300k"
_AI4PRIVACY_REVISION = "c8c77895a005822682b66ab547fc0422579bc1d3"
_NEMOTRON_REPO = "nvidia/Nemotron-PII"
_NEMOTRON_REVISION = "b70ffaf5ff39e079776134c5bf4381f00a9fd1ed"
_TAB_BASE_URL = (
    "https://raw.githubusercontent.com/NorskRegnesentral/text-anonymization-benchmark/"
    "558e09e26d6b36f5f78440074e6a233946d98bd9"
)

## Our dev split samples ai4privacy's train file, our test split its validation file.
AI4PRIVACY_FILES: dict[Split, str] = {
    "dev": "data/train/1english_openpii_30k.jsonl",
    "test": "data/validation/1english_openpii_8k.jsonl",
}
TAB_FILES: dict[Split, str] = {"dev": "echr_dev.json", "test": "echr_test.json"}
## Same scheme as ai4privacy: dev samples the train file, test the test file.
NEMOTRON_FILES: dict[Split, str] = {
    "dev": "data/train-00000-of-00001.parquet",
    "test": "data/test-00000-of-00001.parquet",
}
TAB_EVAL_SCRIPT = "evaluation.py"


def fetch_ai4privacy(data_dir: Path) -> Path:
    """Download the English train and validation files of ai4privacy pii-masking-300k.

    Parameters
    ----------
    data_dir:
        Root data directory; files land in `data_dir / "ai4privacy"`.

    Returns
    -------
    Path
        The dataset directory. Skips files already present.
    """
    target = data_dir / "ai4privacy"
    for filename in AI4PRIVACY_FILES.values():
        hf_hub_download(
            _AI4PRIVACY_REPO,
            filename,
            repo_type="dataset",
            revision=_AI4PRIVACY_REVISION,
            local_dir=target,
        )
    return target


def fetch_nemotron(data_dir: Path) -> Path:
    """Download Nemotron-PII's train and test files (CC BY 4.0).

    Parameters
    ----------
    data_dir:
        Root data directory; files land in `data_dir / "nemotron"`.

    Returns
    -------
    Path
        The dataset directory. Skips files already present.
    """
    target = data_dir / "nemotron"
    for filename in NEMOTRON_FILES.values():
        hf_hub_download(
            _NEMOTRON_REPO,
            filename,
            repo_type="dataset",
            revision=_NEMOTRON_REVISION,
            local_dir=target,
        )
    return target


def fetch_tab(data_dir: Path) -> Path:
    """Download TAB's dev and test splits plus its official `evaluation.py`.

    Parameters
    ----------
    data_dir:
        Root data directory; files land in `data_dir / "tab"`.

    Returns
    -------
    Path
        The dataset directory. Skips files already present.
    """
    target = data_dir / "tab"
    target.mkdir(parents=True, exist_ok=True)
    for filename in (*TAB_FILES.values(), TAB_EVAL_SCRIPT):
        _download_once(f"{_TAB_BASE_URL}/{filename}", target / filename)
    return target


def _download_once(url: str, dest: Path) -> None:
    """Fetch `url` to `dest` unless it exists; a `.part` file keeps interrupted downloads out."""
    if dest.exists():
        return
    partial = dest.with_name(f"{dest.name}.part")
    with httpx.stream("GET", url, follow_redirects=True, timeout=60) as response:
        response.raise_for_status()
        with partial.open("wb") as out:
            for chunk in response.iter_bytes():
                out.write(chunk)
    partial.rename(dest)
