"""Typed failures. Callers catch `PiiBenchError` when the policy is uniform, a subclass when it isn't."""

from __future__ import annotations


class PiiBenchError(Exception):
    """Base for every failure this package raises on purpose."""


class ConfigError(PiiBenchError):
    """Settings are missing or invalid."""


class BudgetExceeded(PiiBenchError):
    """A paid call would push total spend past the project cap."""


class ProviderError(PiiBenchError):
    """A remote model returned an error or an answer we can't parse."""


class AlignmentError(PiiBenchError):
    """An LLM's answer can't be mapped back onto the source text."""


class DataError(PiiBenchError):
    """A dataset breaks an assumption the scoring relies on."""
