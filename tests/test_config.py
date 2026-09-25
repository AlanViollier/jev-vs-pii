"""Settings load from YAML; a bad value fails loudly at startup."""

from __future__ import annotations

from pathlib import Path

import pytest

from pii_bench.config import get_settings
from pii_bench.exceptions import ConfigError


def test_settings_load_from_yaml(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text("project: pii_bench\nconcurrency: 3\n")
    assert get_settings.__wrapped__(config).concurrency == 3


def test_invalid_settings_raise_config_error(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text("concurrency: lots\n")
    with pytest.raises(ConfigError):
        get_settings.__wrapped__(config)
