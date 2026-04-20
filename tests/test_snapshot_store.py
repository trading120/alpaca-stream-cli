"""Tests for SnapshotStore."""

from __future__ import annotations

import pytest

from alpaca_stream_cli.display import QuoteSnapshot
from alpaca_stream_cli.snapshot_store import SnapshotStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snap(symbol: str, price: float = 100.0) -> QuoteSnapshot:
    return QuoteSnapshot(
        symbol=symbol,
        bid=price - 0.01,
        ask=price + 0.01,
        last=price,
        change=0.0,
        change_pct=0.0,
        volume=1_000,
    )


@pytest.fixture()
def store() -> SnapshotStore:
    return SnapshotStore()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_update_and_get(store: SnapshotStore) -> None:
    store.update(_snap("AAPL", 150.0))
    snap = store.get("AAPL")
    assert snap is not None
    assert snap.last == 150.0


def test_get_normalizes_case(store: SnapshotStore) -> None:
    store.update(_snap("aapl", 150.0))
    assert store.get("AAPL") is not None
    assert store.get("aapl") is not None


def test_update_replaces_existing(store: SnapshotStore) -> None:
    store.update(_snap("TSLA", 200.0))
    store.update(_snap("TSLA", 210.0))
    assert store.get("TSLA").last == 210.0
    assert len(store) == 1


def test_get_missing_returns_none(store: SnapshotStore) -> None:
    assert store.get("MISSING") is None


def test_remove_existing(store: SnapshotStore) -> None:
    store.update(_snap("GOOG"))
    assert store.remove("GOOG") is True
    assert store.get("GOOG") is None


def test_remove_missing_returns_false(store: SnapshotStore) -> None:
    assert store.remove("NOPE") is False


def test_all_sorted(store: SnapshotStore) -> None:
    for sym in ["TSLA", "AAPL", "MSFT"]:
        store.update(_snap(sym))
    symbols = [s.symbol for s in store.all()]
    assert symbols == sorted(symbols)


def test_symbols(store: SnapshotStore) -> None:
    store.update(_snap("AAPL"))
    store.update(_snap("GOOG"))
    assert store.symbols() == ["AAPL", "GOOG"]


def test_contains(store: SnapshotStore) -> None:
    store.update(_snap("NVDA"))
    assert "NVDA" in store
    assert "nvda" in store
    assert "AMD" not in store


def test_clear(store: SnapshotStore) -> None:
    store.update(_snap("AAPL"))
    store.update(_snap("GOOG"))
    store.clear()
    assert len(store) == 0


def test_iter(store: SnapshotStore) -> None:
    for sym in ["AAPL", "GOOG", "MSFT"]:
        store.update(_snap(sym))
    result = list(store)
    assert len(result) == 3
