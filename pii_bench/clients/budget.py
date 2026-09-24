"""Project-wide spend ledger. Persisted to disk so the cap covers every run, not each one."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path


class Ledger:
    """Tracks total paid-API spend against a hard cap."""

    def __init__(self, path: Path, cap_usd: Decimal) -> None:
        raise NotImplementedError

    @property
    def spent_usd(self) -> Decimal:
        """Total spent so far, across all runs."""
        raise NotImplementedError

    def check(self, estimate_usd: Decimal) -> None:
        """Raise `BudgetExceeded` if spending `estimate_usd` more would pass the cap.

        Parameters
        ----------
        estimate_usd:
            Upper-bound cost of the call about to be made.
        """
        raise NotImplementedError

    def charge(self, cost_usd: Decimal) -> None:
        """Record the real cost of a finished call and persist the total.

        Parameters
        ----------
        cost_usd:
            Cost reported by the provider.
        """
        raise NotImplementedError
