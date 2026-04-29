"""Volume profile tracker: accumulates traded volume at each price level."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class VolumeProfileResult:
    symbol: str
    levels: Dict[float, float]  # price -> cumulative volume
    poc: Optional[float]        # price of control (highest volume price)
    total_volume: float

    def value_area(self, pct: float = 0.70) -> Tuple[float, float]:
        """Return (low, high) price range containing *pct* of total volume."""
        if not self.levels or self.total_volume == 0:
            return (0.0, 0.0)
        target = self.total_volume * pct
        sorted_levels = sorted(self.levels.items(), key=lambda kv: kv[1], reverse=True)
        accumulated = 0.0
        prices_in_area: List[float] = []
        for price, vol in sorted_levels:
            accumulated += vol
            prices_in_area.append(price)
            if accumulated >= target:
                break
        return (min(prices_in_area), max(prices_in_area))


class _SymbolProfile:
    def __init__(self, tick_size: float) -> None:
        if tick_size <= 0:
            raise ValueError("tick_size must be positive")
        self._tick = tick_size
        self._buckets: Dict[float, float] = defaultdict(float)

    def _bucket(self, price: float) -> float:
        return round(round(price / self._tick) * self._tick, 10)

    def record(self, price: float, volume: float) -> None:
        if price <= 0:
            raise ValueError("price must be positive")
        if volume < 0:
            raise ValueError("volume must be non-negative")
        self._buckets[self._bucket(price)] += volume

    def result(self, symbol: str) -> VolumeProfileResult:
        levels = dict(self._buckets)
        total = sum(levels.values())
        poc = max(levels, key=levels.__getitem__) if levels else None
        return VolumeProfileResult(symbol=symbol, levels=levels, poc=poc, total_volume=total)


class VolumeProfileTracker:
    """Tracks per-symbol intraday volume profiles bucketed by tick size."""

    def __init__(self, tick_size: float = 0.01, max_symbols: int = 100) -> None:
        if tick_size <= 0:
            raise ValueError("tick_size must be positive")
        if max_symbols < 1:
            raise ValueError("max_symbols must be at least 1")
        self._tick = tick_size
        self._max = max_symbols
        self._profiles: Dict[str, _SymbolProfile] = {}

    def record(self, symbol: str, price: float, volume: float) -> VolumeProfileResult:
        key = symbol.upper()
        if key not in self._profiles:
            if len(self._profiles) >= self._max:
                raise OverflowError(f"max_symbols ({self._max}) reached")
            self._profiles[key] = _SymbolProfile(self._tick)
        self._profiles[key].record(price, volume)
        return self._profiles[key].result(key)

    def get(self, symbol: str) -> Optional[VolumeProfileResult]:
        profile = self._profiles.get(symbol.upper())
        return profile.result(symbol.upper()) if profile else None

    def reset(self, symbol: str) -> None:
        self._profiles.pop(symbol.upper(), None)

    def reset_all(self) -> None:
        self._profiles.clear()

    @property
    def symbols(self) -> List[str]:
        return list(self._profiles.keys())
