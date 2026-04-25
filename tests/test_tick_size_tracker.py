"""Tests for alpaca_stream_cli.tick_size_tracker."""
import pytest
from alpaca_stream_cli.tick_size_tracker import SymbolTickSize, TickSizeTracker


# ---------------------------------------------------------------------------
# SymbolTickSize unit tests
# ---------------------------------------------------------------------------

def test_single_price_gives_no_tick():
    s = SymbolTickSize()
    s.record(100.0)
    assert s.min_tick is None


def test_two_prices_computes_tick():
    s = SymbolTickSize()
    s.record(100.00)
    s.record(100.01)
    assert s.min_tick == pytest.approx(0.01)


def test_min_tick_updates_with_smaller_diff():
    s = SymbolTickSize()
    s.record(100.00)
    s.record(100.10)
    s.record(100.11)
    assert s.min_tick == pytest.approx(0.01)


def test_equal_prices_do_not_update_tick():
    s = SymbolTickSize()
    s.record(50.0)
    s.record(50.0)
    assert s.min_tick is None


def test_negative_price_raises():
    s = SymbolTickSize()
    with pytest.raises(ValueError):
        s.record(-1.0)


def test_zero_price_raises():
    s = SymbolTickSize()
    with pytest.raises(ValueError):
        s.record(0.0)


def test_sample_count_increments():
    s = SymbolTickSize()
    for p in [10.0, 10.05, 10.10]:
        s.record(p)
    assert s.sample_count == 3


# ---------------------------------------------------------------------------
# TickSizeTracker integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tracker():
    return TickSizeTracker(max_symbols=10)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        TickSizeTracker(max_symbols=0)


def test_record_returns_none_before_two_prices(tracker):
    result = tracker.record("AAPL", 150.0)
    assert result is None


def test_record_returns_tick_after_two_prices(tracker):
    tracker.record("AAPL", 150.00)
    result = tracker.record("AAPL", 150.01)
    assert result == pytest.approx(0.01)


def test_symbol_normalized_to_uppercase(tracker):
    tracker.record("aapl", 200.0)
    tracker.record("AAPL", 200.05)
    assert tracker.min_tick("aapl") == pytest.approx(0.05)


def test_unknown_symbol_returns_none(tracker):
    assert tracker.min_tick("ZZZZ") is None


def test_unknown_symbol_sample_count_is_zero(tracker):
    assert tracker.sample_count("MSFT") == 0


def test_known_symbols_sorted(tracker):
    tracker.record("TSLA", 700.0)
    tracker.record("AAPL", 150.0)
    tracker.record("MSFT", 300.0)
    assert tracker.known_symbols() == ["AAPL", "MSFT", "TSLA"]


def test_remove_existing_symbol(tracker):
    tracker.record("GOOG", 2800.0)
    removed = tracker.remove("GOOG")
    assert removed is True
    assert tracker.min_tick("GOOG") is None


def test_remove_nonexistent_symbol_returns_false(tracker):
    assert tracker.remove("NOPE") is False


def test_max_symbols_limit_respected():
    t = TickSizeTracker(max_symbols=2)
    t.record("A", 1.0)
    t.record("B", 2.0)
    result = t.record("C", 3.0)
    assert result is None
    assert "C" not in t.known_symbols()
