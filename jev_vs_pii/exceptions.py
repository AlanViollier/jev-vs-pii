"""Typed failures. Callers catch `JevVsPiiError` when the policy is uniform, a subclass when it isn't."""

from __future__ import annotations


class JevVsPiiError(Exception):
    """Base for every failure this package raises on purpose."""


class ConfigError(JevVsPiiError):
    """Settings are missing or invalid."""


class BudgetExceeded(JevVsPiiError):
    """A paid call would push total spend past the project cap."""


class ProviderError(JevVsPiiError):
    """A remote model returned an error or an answer we can't parse."""


class AlignmentError(JevVsPiiError):
    """An LLM's answer can't be mapped back onto the source text."""


class DataError(JevVsPiiError):
    """A dataset breaks an assumption the scoring relies on."""
