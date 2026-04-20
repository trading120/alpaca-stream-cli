"""Tests for the PriceHistory module."""
import time
import pytest
from alpaca_stream_cli.history import PriceHistory, PricePoint


@pytest.fixture
def history() -> PriceHistory:
    return PriceHistory(max_points=10)


def test_record_and_retrieve(history: PriceHistory) -> None:
    history.record("AAPL", 150.0)
    points = history.get("AAPL")
    assert len(points) == 1
    assert points[0].price == 150.0


def test_record_normalizes_lowercase(history: PriceHistory) -> None:
    history.record("aapl", 150.0)
    assert len(history.get("AAPL")) == 1


def test_multiple_records(history: PriceHistory) -> None:
    for price in [100.0, 110.0, 120.0]:
        history.record("TSLA", price)
    points = history.get("TSLA")
    assert len(points) == 3
    assert points[-1].price == 120.0


def test_max_points_respected(history: PriceHistory) -> None:
    for i in range(15):
        history.record("MSFT", float(i))
    assert len(history.get("MSFT")) == 10


def test_latest_returns_most_recent(history: PriceHistory) -> None:
    history.record("GOOG", 200.0)
    history.record("GOOG", 205.0)
    latest = history.latest("GOOG")
    assert latest is not None
    assert latest.price == 205.0


def test_latest_returns_none_for_unknown_symbol(history: PriceHistory) -> None:
    assert history.latest("UNKNOWN") is None


def test_change_pct_positive(history: PriceHistory) -> None:
    history.record("AMZN", 100.0)
    history.record("AMZN", 110.0)
    pct = history.change_pct("AMZN")
    assert pct == pytest.approx(10.0)


def test_change_pct_negative(history: PriceHistory) -> None:
    history.record("AMZN", 200.0)
    history.record("AMZN", 180.0)
    pct = history.change_pct("AMZN")
    assert pct == pytest.approx(-10.0)


def test_change_pct_insufficient_data(history: PriceHistory) -> None:
    history.record("AMZN", 100.0)
    assert history.change_pct("AMZN") is None


def test_change_pct_unknown_symbol(history: PriceHistory) -> None:
    assert history.change_pct("XYZ") is None


def test_clear_symbol(history: PriceHistory) -> None:
    history.record("NVDA", 300.0)
    history.clear("NVDA")
    assert history.get("NVDA") == []


def test_clear_all(history: PriceHistory) -> None:
    history.record("AAPL", 150.0)
    history.record("TSLA", 700.0)
    history.clear_all()
    assert history.tracked_symbols == []


def test_tracked_symbols(history: PriceHistory) -> None:
    history.record("AAPL", 150.0)
    history.record("TSLA", 700.0)
    assert set(history.tracked_symbols) == {"AAPL", "TSLA"}


def test_price_point_has_timestamp() -> None:
    before = time.time()
    point = PricePoint(price=99.9)
    after = time.time()
    assert before <= point.timestamp <= after
