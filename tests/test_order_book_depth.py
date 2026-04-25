"""Tests for OrderBookDepth."""
import pytest
from alpaca_stream_cli.order_book_depth import OrderBookDepth, BookSnapshot, DepthLevel


@pytest.fixture
def book():
    return OrderBookDepth(max_levels=3, max_symbols=10)


def test_invalid_max_levels_raises():
    with pytest.raises(ValueError):
        OrderBookDepth(max_levels=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        OrderBookDepth(max_symbols=0)


def test_update_returns_snapshot(book):
    snap = book.update("AAPL", [(150.0, 100), (149.9, 200)], [(150.1, 50)])
    assert isinstance(snap, BookSnapshot)
    assert snap.symbol == "AAPL"


def test_update_normalizes_symbol_to_uppercase(book):
    book.update("aapl", [(150.0, 100)], [(150.1, 50)])
    assert book.get("AAPL") is not None
    assert book.get("aapl") is not None


def test_best_bid_and_ask(book):
    snap = book.update("TSLA", [(200.0, 10), (199.5, 20)], [(200.5, 5), (201.0, 15)])
    assert snap.best_bid.price == 200.0
    assert snap.best_ask.price == 200.5


def test_best_bid_none_when_empty(book):
    snap = book.update("MSFT", [], [(300.1, 10)])
    assert snap.best_bid is None


def test_best_ask_none_when_empty(book):
    snap = book.update("MSFT", [(300.0, 10)], [])
    assert snap.best_ask is None


def test_max_levels_respected(book):
    bids = [(100.0 - i * 0.1, 10) for i in range(10)]
    asks = [(100.1 + i * 0.1, 10) for i in range(10)]
    snap = book.update("GOOG", bids, asks)
    assert len(snap.bids) == 3
    assert len(snap.asks) == 3


def test_total_bid_size(book):
    snap = book.update("NVDA", [(50.0, 100), (49.9, 200), (49.8, 300)], [])
    assert snap.total_bid_size == 600


def test_total_ask_size(book):
    snap = book.update("NVDA", [], [(50.1, 50), (50.2, 75)])
    assert snap.total_ask_size == 125


def test_get_returns_none_for_unknown(book):
    assert book.get("UNKNOWN") is None


def test_remove_existing_symbol(book):
    book.update("AMD", [(80.0, 10)], [(80.1, 5)])
    assert book.remove("AMD") is True
    assert book.get("AMD") is None


def test_remove_nonexistent_returns_false(book):
    assert book.remove("FAKE") is False


def test_symbols_lists_tracked_symbols(book):
    book.update("AAPL", [(1.0, 1)], [(1.1, 1)])
    book.update("TSLA", [(2.0, 1)], [(2.1, 1)])
    assert set(book.symbols()) == {"AAPL", "TSLA"}


def test_clear_removes_all(book):
    book.update("AAPL", [(1.0, 1)], [(1.1, 1)])
    book.clear()
    assert book.symbols() == []
