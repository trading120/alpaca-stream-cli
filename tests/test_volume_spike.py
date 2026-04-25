"""Tests for VolumeSpikeTracker and SymbolVolumeSpike."""
import pytest
from alpaca_stream_cli.volume_spike import (
    SymbolVolumeSpike,
    VolumeSpikeTracker,
    VolumeSpikeResult,
)


# --- SymbolVolumeSpike ---

def test_invalid_window_raises():
    with pytest.raises(ValueError):
        SymbolVolumeSpike(window=0)


def test_invalid_multiplier_raises():
    with pytest.raises(ValueError):
        SymbolVolumeSpike(spike_multiplier=0)


def test_baseline_none_when_empty():
    s = SymbolVolumeSpike()
    assert s.baseline() is None


def test_baseline_after_records():
    s = SymbolVolumeSpike(window=4)
    for v in [100.0, 200.0, 300.0, 400.0]:
        s.record(v)
    assert s.baseline() == pytest.approx(250.0)


def test_window_limits_samples():
    s = SymbolVolumeSpike(window=3)
    for v in [10.0, 20.0, 30.0, 1000.0]:
        s.record(v)
    # only last 3 retained: 20, 30, 1000
    assert s.baseline() == pytest.approx((20 + 30 + 1000) / 3)


def test_is_spike_false_with_no_baseline():
    s = SymbolVolumeSpike(spike_multiplier=2.0)
    assert s.is_spike(9999.0) is False


def test_is_spike_true_when_above_multiplier():
    s = SymbolVolumeSpike(window=4, spike_multiplier=2.0)
    for v in [100.0, 100.0, 100.0, 100.0]:
        s.record(v)
    assert s.is_spike(200.0) is True


def test_is_spike_false_when_below_multiplier():
    s = SymbolVolumeSpike(window=4, spike_multiplier=2.0)
    for v in [100.0, 100.0, 100.0, 100.0]:
        s.record(v)
    assert s.is_spike(199.0) is False


# --- VolumeSpikeTracker ---

@pytest.fixture
def tracker():
    return VolumeSpikeTracker(window=5, spike_multiplier=2.0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        VolumeSpikeTracker(max_symbols=0)


def test_record_returns_result(tracker):
    result = tracker.record("aapl", 500.0)
    assert isinstance(result, VolumeSpikeResult)
    assert result.symbol == "AAPL"


def test_record_normalizes_symbol(tracker):
    result = tracker.record("msft", 100.0)
    assert result.symbol == "MSFT"


def test_no_spike_on_first_record(tracker):
    result = tracker.record("AAPL", 1000.0)
    assert result.is_spike is False


def test_spike_detected_after_baseline(tracker):
    for _ in range(5):
        tracker.record("AAPL", 100.0)
    result = tracker.record("AAPL", 300.0)
    assert result.is_spike is True


def test_ratio_calculated_correctly(tracker):
    for _ in range(5):
        tracker.record("TSLA", 200.0)
    result = tracker.record("TSLA", 400.0)
    assert result.ratio == pytest.approx(2.0, rel=0.1)


def test_remove_symbol(tracker):
    tracker.record("GOOG", 100.0)
    assert "GOOG" in tracker.symbols()
    tracker.remove("goog")
    assert "GOOG" not in tracker.symbols()


def test_max_symbols_evicts_oldest():
    t = VolumeSpikeTracker(window=3, spike_multiplier=2.0, max_symbols=2)
    t.record("AAA", 1.0)
    t.record("BBB", 1.0)
    t.record("CCC", 1.0)  # should evict AAA
    syms = t.symbols()
    assert "AAA" not in syms
    assert "BBB" in syms
    assert "CCC" in syms
