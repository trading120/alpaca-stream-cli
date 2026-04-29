"""Tests for SupportResistanceTracker and sr_display."""
import pytest
from alpaca_stream_cli.support_resistance import SupportResistanceTracker, SRResult
from alpaca_stream_cli.sr_display import build_sr_table, _fmt_price, _fmt_distance, _level_color


@pytest.fixture
def tracker():
    return SupportResistanceTracker(max_pivots=10)


def test_invalid_max_pivots_raises():
    with pytest.raises(ValueError, match="max_pivots"):
        SupportResistanceTracker(max_pivots=1)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError, match="max_symbols"):
        SupportResistanceTracker(max_symbols=0)


def test_record_returns_sr_result(tracker):
    result = tracker.record("AAPL", 150.0)
    assert isinstance(result, SRResult)
    assert result.symbol == "AAPL"
    assert result.last_price == 150.0


def test_record_normalizes_symbol_to_uppercase(tracker):
    result = tracker.record("aapl", 150.0)
    assert result.symbol == "AAPL"


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError):
        tracker.record("AAPL", -1.0)


def test_support_is_min_price(tracker):
    for price in [150.0, 148.0, 152.0, 149.0]:
        tracker.record("AAPL", price)
    result = tracker.result("AAPL")
    assert result.support == pytest.approx(148.0)


def test_resistance_is_max_price(tracker):
    for price in [150.0, 148.0, 155.0, 149.0]:
        tracker.record("AAPL", price)
    result = tracker.result("AAPL")
    assert result.resistance == pytest.approx(155.0)


def test_result_none_for_unknown_symbol(tracker):
    assert tracker.result("ZZZZ") is None


def test_near_support_true_when_close(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("AAPL", 148.0)
    result = tracker.record("AAPL", 148.3)  # within 0.5% of 148.0
    assert result.near_support is True


def test_near_resistance_true_when_close(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("AAPL", 155.0)
    result = tracker.record("AAPL", 154.8)  # within 0.5% of 155.0
    assert result.near_resistance is True


def test_symbols_list_returns_tracked(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("TSLA", 200.0)
    assert set(tracker.symbols()) == {"AAPL", "TSLA"}


def test_fmt_price_none():
    assert _fmt_price(None) == "--"


def test_fmt_price_value():
    assert _fmt_price(150.5) == "$150.50"


def test_fmt_distance_none():
    assert _fmt_distance(None, 100.0) == "--"
    assert _fmt_distance(100.0, None) == "--"


def test_fmt_distance_positive():
    result = _fmt_distance(100.0, 105.0)
    assert "+" in result
    assert "5.00%" in result


def test_level_color_dim_when_none():
    assert _level_color(None, 100.0, True) == "dim"


def test_level_color_yellow_when_near():
    assert _level_color(100.0, 100.2, True) == "bold yellow"


def test_build_sr_table_returns_table(tracker):
    from rich.table import Table
    tracker.record("AAPL", 150.0)
    table = build_sr_table(["AAPL"], tracker)
    assert isinstance(table, Table)


def test_build_sr_table_row_count(tracker):
    for sym in ["AAPL", "TSLA", "MSFT"]:
        tracker.record(sym, 100.0)
    table = build_sr_table(["AAPL", "TSLA", "MSFT"], tracker)
    assert table.row_count == 3


def test_build_sr_table_unknown_symbol_renders_placeholder(tracker):
    table = build_sr_table(["UNKNOWN"], tracker)
    assert table.row_count == 1


def test_build_sr_table_has_seven_columns(tracker):
    table = build_sr_table([], tracker)
    assert len(table.columns) == 7
