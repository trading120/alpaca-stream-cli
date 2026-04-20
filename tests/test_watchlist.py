"""Tests for the Watchlist class."""

import pytest
from alpaca_stream_cli.watchlist import Watchlist


def test_add_valid_symbol():
    wl = Watchlist()
    assert wl.add("AAPL") is True
    assert "AAPL" in wl


def test_add_duplicate_returns_false():
    wl = Watchlist(["MSFT"])
    assert wl.add("MSFT") is False
    assert len(wl) == 1


def test_add_normalizes_lowercase():
    wl = Watchlist()
    wl.add("tsla")
    assert "TSLA" in wl


def test_add_invalid_symbol_raises():
    wl = Watchlist()
    with pytest.raises(ValueError):
        wl.add("TOOLONG")
    with pytest.raises(ValueError):
        wl.add("123")
    with pytest.raises(ValueError):
        wl.add("")


def test_remove_existing_symbol():
    wl = Watchlist(["AAPL", "GOOG"])
    assert wl.remove("AAPL") is True
    assert "AAPL" not in wl
    assert len(wl) == 1


def test_remove_nonexistent_returns_false():
    wl = Watchlist(["AAPL"])
    assert wl.remove("NFLX") is False


def test_list_returns_copy():
    wl = Watchlist(["AAPL", "MSFT"])
    result = wl.list()
    result.append("FAKE")
    assert "FAKE" not in wl


def test_init_with_symbols():
    wl = Watchlist(["AAPL", "MSFT", "TSLA"])
    assert len(wl) == 3
