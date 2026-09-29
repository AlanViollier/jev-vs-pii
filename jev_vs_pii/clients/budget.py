"""Project-wide spend ledger. Persisted to disk so the cap covers every run, not each one."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

from jev_vs_pii.exceptions import BudgetExceeded


class Ledger:
    """Tracks total paid-API spend against a hard cap.

    Calls in flight hold their estimate until they settle, so concurrent calls can't
    all pass the check before any of them is charged.
    """

    def __init__(self, path: Path, cap_usd: Decimal) -> None:
        self._path = path
        self._cap = cap_usd
        self._held = Decimal(0)
        self._spent = (
            Decimal(json.loads(path.read_text())["spent_usd"]) if path.exists() else Decimal(0)
        )

    @property
    def spent_usd(self) -> Decimal:
        """Total spent so far, across all runs."""
        return self._spent

    @contextmanager
    def reserve(self, estimate_usd: Decimal) -> Iterator[Callable[[Decimal], None]]:
        """Hold `estimate_usd` for one call; the caller charges the real cost inside.

        Parameters
        ----------
        estimate_usd:
            Upper-bound cost of the call about to be made.

        Returns
        -------
        Iterator[Callable[[Decimal], None]]
            Yields `charge`. Raises `BudgetExceeded` before yielding if spent + held +
            estimate would pass the cap. The hold is released however the block exits.
        """
        if self._spent + self._held + estimate_usd > self._cap:
            raise BudgetExceeded(
                f"spent ${self._spent} + in flight ${self._held} + next ${estimate_usd} "
                f"would pass the ${self._cap} cap"
            )
        self._held += estimate_usd
        try:
            yield self.charge
        finally:
            self._held -= estimate_usd

    def charge(self, cost_usd: Decimal) -> None:
        """Record the real cost of a finished call and persist the total.

        Parameters
        ----------
        cost_usd:
            Cost reported by the provider.
        """
        self._spent += cost_usd
        self._path.parent.mkdir(parents=True, exist_ok=True)
        partial = self._path.with_name(f"{self._path.name}.part")
        partial.write_text(json.dumps({"spent_usd": str(self._spent)}))
        partial.replace(self._path)
