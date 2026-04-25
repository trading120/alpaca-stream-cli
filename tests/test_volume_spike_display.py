"""Tests for volume spike display helpers."""
import pytest
from rich.table import Table
from alpaca_stream_cli.volume_spike import VolumeSpikeResult
from alpaca_stream_cli.volume_spike_display import (
    _spike_color,
    _fmt_ratio,
    _fmt_volume,
    build_volume_spike_table,
)


def _result(symbol: str, current: float, baseline: float, ratio: float, spike: bool) -> VolumeSpikeResult:
    return VolumeSpikeResult(
        symbol=symbol,
        current_volume=current,
        baseline_volume=baseline,
        ratio=ratio,
        is_spike=spike,
    )


# --- _spike_color ---

def test_spike_color_high_ratio_is_bold_red():
    assert _spike_color(4.0) == "bold red"


def test_spike_color_medium_ratio_is_yellow():
    assert _spike_color(2.5) == "yellow"


def test_spike_color_low_ratio_is_green():
    assert _spike_color(1.5) == "green"


def test_spike_color_below_one_is_dim():
    assert _spike_color(0.5) == "dim"


# --- _fmt_ratio ---

def test_fmt_ratio_none_returns_dashes():
    assert _fmt_ratio(None) == "--"


def test_fmt_ratio_formats_with_x():
    assert _fmt_ratio(3.14) == "3.14x"


# --- _fmt_volume ---

def test_fmt_volume_none_returns_dashes():
    assert _fmt_volume(None) == "--"


def test_fmt_volume_millions():
    assert "M" in _fmt_volume(2_500_000)


def test_fmt_volume_thousands():
    assert "K" in _fmt_volume(15_000)


def test_fmt_volume_small():
    result = _fmt_volume(42.0)
    assert result == "42"


# --- build_volume_spike_table ---

@pytest.fixture
def sample_results():
    return {
        "AAPL": _result("AAPL", 500_000, 200_000, 2.5, True),
        "TSLA": _result("TSLA", 100_000, 150_000, 0.67, False),
        "MSFT": _result("MSFT", 1_000_000, 250_000, 4.0, True),
    }


def test_build_volume_spike_table_returns_table(sample_results):
    table = build_volume_spike_table(sample_results)
    assert isinstance(table, Table)


def test_table_has_five_columns(sample_results):
    table = build_volume_spike_table(sample_results)
    assert len(table.columns) == 5


def test_table_row_count_matches_input(sample_results):
    table = build_volume_spike_table(sample_results)
    assert table.row_count == len(sample_results)


def test_table_respects_max_rows(sample_results):
    table = build_volume_spike_table(sample_results, max_rows=2)
    assert table.row_count == 2


def test_empty_results_produces_empty_table():
    table = build_volume_spike_table({})
    assert table.row_count == 0
