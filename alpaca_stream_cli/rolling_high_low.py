"""Tracks rolling high/low prices over a configurable time window per symbol."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RollingHLResult:
    symbol: str
    high: float
    low: float
    window_seconds: int
    sample_count: int

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def range_pct(self) -> Optional[float]:
        if self.low == 0:
            return None
        return (self.range / self.low) * 100.0


@dataclass
class _Tick:
    ts: datetime
    price: float


@dataclass
class SymbolRollingHL:
    window_seconds: int
    _ticks: deque = field(default_factory=deque, init=False)

    def record(self, price: float, ts: Optional[datetime] = None) -> RollingHLResult:
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")
        now = ts or datetime.utcnow()
        self._ticks.append(_Tick(ts=now, price=price))
        self._evict(now)
        prices = [t.price for t in self._ticks]
        return RollingHLResult(
            symbol="",
            high=max(prices),
            low=min(prices),
            window_seconds=self.window_seconds,
            sample_count=len(prices),
        )

    def _evict(self, now: datetime) -> None:
        cutoff = now.timestamp() - self.window_seconds
        while self._ticks and self._ticks[0].ts.timestamp() < cutoff:
            self._ticks.popleft()


class RollingHighLowTracker:
    """Tracks rolling high/low for multiple symbols."""

    def __init__(self, window_seconds: int = 300, max_symbols: int = 200) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if max_symbols <= 0:
            raise ValueError("max_symbols must be positive")
        self._window = window_seconds
        self._max = max_symbols
        self._symbols: dict[str, SymbolRollingHL] = {}

    def record(self, symbol: str, price: float, ts: Optional[datetime] = None) -> RollingHLResult:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max:
                raise RuntimeError(f"max_symbols ({self._max}) reached")
            self._symbols[key] = SymbolRollingHL(window_seconds=self._window)
        result = self._symbols[key].record(price, ts)
        result.symbol = key
        return result

    def get(self, symbol: str) -> Optional[RollingHLResult]:
        key = symbol.upper()
        if key not in self._symbols:
            return None
        sym = self._symbols[key]
        if not sym._ticks:
            return None
        prices = [t.price for t in sym._ticks]
        return RollingHLResult(
            symbol=key,
            high=max(prices),
            low=min(prices),
            window_seconds=self._window,
            sample_count=len(prices),
        )

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
