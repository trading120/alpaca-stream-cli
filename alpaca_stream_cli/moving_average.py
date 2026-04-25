"""Simple moving average tracker for symbol prices."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional


@dataclass
class SymbolMA:
    """Maintains a rolling window of prices for one symbol."""

    period: int
    _prices: Deque[float] = field(default_factory=deque, init=False)

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError(f"Price must be non-negative, got {price}")
        self._prices.append(price)
        if len(self._prices) > self.period:
            self._prices.popleft()

    def value(self) -> Optional[float]:
        """Return the simple moving average, or None if not enough data."""
        if len(self._prices) < self.period:
            return None
        return sum(self._prices) / len(self._prices)

    def sample_count(self) -> int:
        return len(self._prices)


class MovingAverageTracker:
    """Tracks SMA for multiple symbols across one or two periods."""

    def __init__(
        self,
        short_period: int = 10,
        long_period: int = 20,
        max_symbols: int = 200,
    ) -> None:
        if short_period < 1:
            raise ValueError("short_period must be >= 1")
        if long_period < short_period:
            raise ValueError("long_period must be >= short_period")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._short = short_period
        self._long = long_period
        self._max = max_symbols
        self._short_ma: Dict[str, SymbolMA] = {}
        self._long_ma: Dict[str, SymbolMA] = {}

    def record(self, symbol: str, price: float) -> None:
        key = symbol.upper()
        if key not in self._short_ma:
            if len(self._short_ma) >= self._max:
                raise OverflowError(f"Tracking limit of {self._max} symbols reached")
            self._short_ma[key] = SymbolMA(self._short)
            self._long_ma[key] = SymbolMA(self._long)
        self._short_ma[key].record(price)
        self._long_ma[key].record(price)

    def short_ma(self, symbol: str) -> Optional[float]:
        return self._short_ma.get(symbol.upper(), SymbolMA(self._short)).value()

    def long_ma(self, symbol: str) -> Optional[float]:
        return self._long_ma.get(symbol.upper(), SymbolMA(self._long)).value()

    def crossover(self, symbol: str) -> Optional[bool]:
        """Return True if short MA > long MA, False if below, None if unavailable."""
        s = self.short_ma(symbol)
        l = self.long_ma(symbol)
        if s is None or l is None:
            return None
        return s > l

    def symbols(self) -> list[str]:
        return list(self._short_ma.keys())
