"""Tests for rolling_high_low and rolling_hl_display."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from rich.table import Table

from alpaca_stream_cli.rolling_high_low import (
    RollingHighLowTracker,
    RollingHLResult,
)
from alpaca_stream_cli.rolling_hl_display import build_rolling_hl_table, _range_color


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(offset_seconds: float = 0.0) -> datetime:
    base = datetime(2024, 1, 15, 12, 0, 0)
    return base + timedelta(seconds=offset_seconds)


@pytest.fixture()
def tracker() -> RollingHighLowTracker:
    return RollingHighLowTracker(window_seconds=60, max_symbols=10)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_invalid_window_raises():
    with pytest.raises(ValueError):
        RollingHighLowTracker(window_seconds=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        RollingHighLowTracker(max_symbols=0)


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError):
        tracker.record("AAPL", -1.0, _ts())


def test_zero_price_raises(tracker):
    with pytest.raises(ValueError):
        tracker.record("AAPL", 0.0, _ts())


# ---------------------------------------------------------------------------
# Core behaviour
# ---------------------------------------------------------------------------

def test_record_returns_result(tracker):
    result = tracker.record("AAPL", 150.0, _ts())
    assert isinstance(result, RollingHLResult)


def test_record_normalizes_symbol_to_uppercase(tracker):
    result = tracker.record("aapl", 150.0, _ts())
    assert result.symbol == "AAPL"


def test_single_record_high_equals_low(tracker):
    result = tracker.record("AAPL", 150.0, _ts())
    assert result.high == 150.0
    assert result.low == 150.0


def test_high_low_tracked_across_records(tracker):
    tracker.record("AAPL", 150.0, _ts(0))
    tracker.record("AAPL", 155.0, _ts(1))
    result = tracker.record("AAPL", 148.0, _ts(2))
    assert result.high == 155.0
    assert result.low == 148.0


def test_range_equals_high_minus_low(tracker):
    tracker.record("AAPL", 100.0, _ts(0))
    result = tracker.record("AAPL", 110.0, _ts(1))
    assert result.range == pytest.approx(10.0)


def test_range_pct_calculated_correctly(tracker):
    tracker.record("AAPL", 100.0, _ts(0))
    result = tracker.record("AAPL", 110.0, _ts(1))
    # range=10, low=100 -> 10%
    assert result.range_pct == pytest.approx(10.0)


def test_old_ticks_evicted_outside_window(tracker):
    tracker.record("AAPL", 200.0, _ts(0))   # will be evicted
    result = tracker.record("AAPL", 150.0, _ts(120))  # 120s later, outside 60s window
    assert result.high == 150.0
    assert result.low == 150.0
    assert result.sample_count == 1


def test_sample_count_reflects_window(tracker):
    for i in range(5):
        tracker.record("AAPL", 100.0 + i, _ts(i * 10))
    result = tracker.get("AAPL")
    assert result.sample_count == 5


def test_get_before_any_data_returns_none(tracker):
    assert tracker.get("MSFT") is None


def test_symbols_list_contains_recorded_symbols(tracker):
    tracker.record("AAPL", 150.0, _ts())
    tracker.record("MSFT", 300.0, _ts())
    assert set(tracker.symbols()) == {"AAPL", "MSFT"}


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def test_build_rolling_hl_table_returns_table(tracker):
    tracker.record("AAPL", 150.0, _ts())
    table = build_rolling_hl_table(tracker)
    assert isinstance(table, Table)


def test_table_has_six_columns(tracker):
    tracker.record("AAPL", 150.0, _ts())
    table = build_rolling_hl_table(tracker)
    assert len(table.columns) == 6


def test_table_row_count_matches_symbols(tracker):
    tracker.record("AAPL", 150.0, _ts())
    tracker.record("MSFT", 300.0, _ts())
    table = build_rolling_hl_table(tracker)
    assert table.row_count == 2


def test_unknown_symbol_renders_placeholder(tracker):
    table = build_rolling_hl_table(tracker, symbols=["ZZZZ"])
    assert table.row_count == 1


def test_range_color_high_is_bold_red():
    assert _range_color(4.0) == "bold red"


def test_range_color_medium_is_yellow():
    assert _range_color(2.0) == "yellow"


def test_range_color_low_is_green():
    assert _range_color(0.8) == "green"


def test_range_color_flat_is_dim():
    assert _range_color(0.1) == "dim"


def test_range_color_none_is_dim():
    assert _range_color(None) == "dim"
