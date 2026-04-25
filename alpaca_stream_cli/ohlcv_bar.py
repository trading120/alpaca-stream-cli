"""OHLCV bar aggregation for intraday candle tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class OHLCVBar:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    bar_time: datetime

    @property
    def change(self) -> float:
        return self.close - self.open

    @property
    def change_pct(self) -> float:
        if self.open == 0:
            return 0.0
        return (self.change / self.open) * 100.0

    @property
    def range(self) -> float:
        return self.high - self.low


@dataclass
class _MutableBar:
    open: float
    high: float
    low: float
    close: float
    volume: float
    bar_time: datetime


class OHLCVTracker:
    """Aggregates trade ticks into OHLCV bars per symbol."""

    def __init__(self, max_symbols: int = 200) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max = max_symbols
        self._bars: Dict[str, _MutableBar] = {}

    def record(self, symbol: str, price: float, volume: float,
               ts: Optional[datetime] = None) -> OHLCVBar:
        """Record a trade tick and return the current bar snapshot."""
        key = symbol.upper()
        now = ts or datetime.now(timezone.utc)
        if key not in self._bars:
            if len(self._bars) >= self._max:
                oldest = next(iter(self._bars))
                del self._bars[oldest]
            self._bars[key] = _MutableBar(
                open=price, high=price, low=price,
                close=price, volume=volume, bar_time=now
            )
        else:
            bar = self._bars[key]
            bar.high = max(bar.high, price)
            bar.low = min(bar.low, price)
            bar.close = price
            bar.volume += volume
        b = self._bars[key]
        return OHLCVBar(key, b.open, b.high, b.low, b.close, b.volume, b.bar_time)

    def get(self, symbol: str) -> Optional[OHLCVBar]:
        key = symbol.upper()
        b = self._bars.get(key)
        if b is None:
            return None
        return OHLCVBar(key, b.open, b.high, b.low, b.close, b.volume, b.bar_time)

    def reset(self, symbol: str) -> None:
        self._bars.pop(symbol.upper(), None)

    def symbols(self) -> list[str]:
        return list(self._bars.keys())
