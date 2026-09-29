"""Single entry point for settings: config.yaml for shape, .env for secrets."""

from __future__ import annotations

from decimal import Decimal
from functools import cache
from pathlib import Path

import yaml
from pydantic import BaseModel, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from pii_bench.exceptions import ConfigError


class ModelSpec(BaseModel):
    """A generative model on OpenRouter and its list prices, which bound the budget hold per call.

    `reasoning` switches thinking on or off for models that can do both; None leaves the
    provider's default. `providers` restricts calls to these OpenRouter providers, for
    comparisons whose runs must share the same serving stack.
    """

    id: str
    input_usd_per_m: Decimal
    output_usd_per_m: Decimal
    reasoning: bool | None = None
    providers: list[str] | None = None


class AppSettings(BaseSettings):
    """Typed settings. Built by `get_settings()`; tests construct it directly.

    `models` maps the short key used in lane ids (`llm_sayback:qwen3-30b`) to a model.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: SecretStr = SecretStr("")
    jev_model: str = "typesafe/jev-1.13"
    budget_cap_usd: Decimal = Decimal("2.00")
    concurrency: int = 8
    seed: int = 0
    data_dir: Path = Path("data")
    cache_dir: Path = Path(".cache")
    runs_dir: Path = Path("runs")
    models: dict[str, ModelSpec] = {}


@cache
def get_settings(config_path: Path = Path("config.yaml")) -> AppSettings:
    """Load settings from `config_path` plus the environment.

    Parameters
    ----------
    config_path:
        YAML file holding non-secret settings.

    Returns
    -------
    AppSettings
        Validated settings; raises `ConfigError` when the file doesn't validate.
    """
    values = yaml.safe_load(config_path.read_text()) or {}
    try:
        return AppSettings(**values)
    except ValidationError as error:
        raise ConfigError(f"{config_path}: {error}") from error
