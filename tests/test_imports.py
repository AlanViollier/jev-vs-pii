"""Every module imports and the CLI lists its commands."""

from __future__ import annotations

import importlib
import pkgutil

from typer.testing import CliRunner

import pii_bench
from pii_bench.cli import app


def test_every_module_imports() -> None:
    for module in pkgutil.walk_packages(pii_bench.__path__, prefix="pii_bench."):
        importlib.import_module(module.name)


def test_cli_lists_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("fetch", "run", "tune", "score", "report"):
        assert command in result.output
