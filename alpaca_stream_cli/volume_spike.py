"""Detects volume spikes relative to a rolling baseline for each symbol."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional


_DEFAULT_WINDOW = 20
_DEFAULT_SPIKE_MULTIPLIER = 2.0


@dataclass
class VolumeSpikeResult:
    symbol: str
    current_volume: float
    baseline_volume: float
    ratio: float
    is_spike: bool


class SymbolVolumeSpike:
    """Tracks rolling volume and detects spikes for a single symbol."""

    def __init__(self, window: int = _DEFAULT_WINDOW, spike_multiplier: float = _DEFAULT_SPIKE_MULTIPLIER) -> None:
        if window < 1:
            raise ValueError(f"window must be >= 1, got {window}")
        if spike_multiplier <= 0:
            raise ValueError(f"spike_multiplier must be > 0, got {spike_multiplier}")
        self._window = window
        self._multiplier = spike_multiplier
        self._samples: Deque[float] = deque(maxlen=window)

    def record(self, volume: float) -> Optional[float]:
        """Record a volume sample. Returns the baseline (mean) if enough data, else None."""
        if self._samples:
            baseline = sum(self._samples) / len(self._samples)
        else:
            baseline = None
        self._samples.append(volume)
        return baseline

    def baseline(self) -> Optional[float]:
        if not self._samples:
            return None
        return sum(self._samples) / len(self._samples)

    def is_spike(self, volume: float) -> bool:
        bl = self.baseline()
        if bl is None or bl == 0:
            return False
        return volume >= bl * self._multiplier


class VolumeSpikeTracker:
    """Manages per-symbol volume spike detection."""

    def __init__(self, window: int = _DEFAULT_WINDOW, spike_multiplier: float = _DEFAULT_SPIKE_MULTIPLIER, max_symbols: int = 500) -> None:
        if max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {max_symbols}")
        self._window = window
        self._multiplier = spike_multiplier
        self._max_symbols = max_symbols
        self._trackers: Dict[str, SymbolVolumeSpike] = {}

    def _get_or_create(self, symbol: str) -> SymbolVolumeSpike:
        key = symbol.upper()
        if key not in self._trackers:
            if len(self._trackers) >= self._max_symbols:
                oldest = next(iter(self._trackers))
                del self._trackers[oldest]
            self._trackers[key] = SymbolVolumeSpike(self._window, self._multiplier)
        return self._trackers[key]

    def record(self, symbol: str, volume: float) -> VolumeSpikeResult:
        key = symbol.upper()
        tracker = self._get_or_create(key)
        baseline_before = tracker.baseline()
        tracker.record(volume)
        baseline = tracker.baseline() or 0.0
        ratio = (volume / baseline) if baseline > 0 else 0.0
        spike = tracker.is_spike(volume) if baseline_before is not None else False
        return VolumeSpikeResult(
            symbol=key,
            current_volume=volume,
            baseline_volume=baseline,
            ratio=ratio,
            is_spike=spike,
        )

    def remove(self, symbol: str) -> None:
        self._trackers.pop(symbol.upper(), None)

    def symbols(self) -> list[str]:
        return list(self._trackers.keys())
