"""The ledger refuses calls past the cap, counts calls in flight, and survives restarts."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from jev_vs_pii.clients.budget import Ledger
from jev_vs_pii.exceptions import BudgetExceeded


def test_charges_persist_across_ledgers(tmp_path: Path) -> None:
    path = tmp_path / "ledger.json"
    ledger = Ledger(path, cap_usd=Decimal("1"))
    with ledger.reserve(Decimal("0.1")) as charge:
        charge(Decimal("0.000018396"))
    assert Ledger(path, cap_usd=Decimal("1")).spent_usd == Decimal("0.000018396")


def test_refuses_a_call_that_could_pass_the_cap(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.json", cap_usd=Decimal("0.5"))
    ledger.charge(Decimal("0.45"))
    with pytest.raises(BudgetExceeded), ledger.reserve(Decimal("0.06")):
        pass


def test_calls_in_flight_count_against_the_cap(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.json", cap_usd=Decimal("1"))
    with (
        ledger.reserve(Decimal("0.6")),
        pytest.raises(BudgetExceeded),
        ledger.reserve(Decimal("0.6")),
    ):
        pass


def test_a_failed_call_releases_its_hold(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.json", cap_usd=Decimal("1"))
    with pytest.raises(RuntimeError), ledger.reserve(Decimal("0.9")):
        raise RuntimeError("provider down")
    with ledger.reserve(Decimal("0.9")) as charge:
        charge(Decimal("0.01"))
    assert ledger.spent_usd == Decimal("0.01")
