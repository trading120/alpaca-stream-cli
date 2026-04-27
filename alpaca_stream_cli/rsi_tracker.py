"""Relative Strength Index (RSI) tracker for per-symbol price streams."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SymbolRSI:
    """Computes RSI for a single symbol using Wilder's smoothing method."""

    period: int = 14
    _gains: list[float] = field(default_factory=list, repr=False)
    _losses: list[float] = field(default_factory=list, repr=False)
    _prev_price: Optional[float] = field(default=None, repr=False)
    _avg_gain: Optional[float] = field(default=None, repr=False)
    _avg_loss: Optional[float] = field(default=None, repr=False)
    _trade_count: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        if self.period < 2:
            raise ValueError(f"period must be >= 2, got {self.period}")

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError(f"price must be non-negative, got {price}")
        if self._prev_price is None:
            self._prev_price = price
            return

        change = price - self._prev_price
        self._prev_price = price
        gain = max(change, 0.0)
        loss = max(-change, 0.0)

        if self._avg_gain is None:
            self._gains.append(gain)
            self._losses.append(loss)
            if len(self._gains) >= self.period:
                self._avg_gain = sum(self._gains) / self.period
                self._avg_loss = sum(self._losses) / self.period
                self._gains.clear()
                self._losses.clear()
        else:
            self._avg_gain = (self._avg_gain * (self.period - 1) + gain) / self.period
            self._avg_loss = (self._avg_loss * (self.period - 1) + loss) / self.period

        self._trade_count += 1

    @property
    def value(self) -> Optional[float]:
        if self._avg_gain is None or self._avg_loss is None:
            return None
        if self._avg_loss == 0.0:
            return 100.0
        rs = self._avg_gain / self._avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    @property
    def trade_count(self) -> int:
        return self._trade_count


class RSITracker:
    """Manages RSI computation across multiple symbols."""

    def __init__(self, period: int = 14, max_symbols: int = 500) -> None:
        if period < 2:
            raise ValueError(f"period must be >= 2, got {period}")
        if max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {max_symbols}")
        self._period = period
        self._max_symbols = max_symbols
        self._symbols: dict[str, SymbolRSI] = {}

    def record(self, symbol: str, price: float) -> None:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                return
            self._symbols[key] = SymbolRSI(period=self._period)
        self._symbols[key].record(price)

    def value(self, symbol: str) -> Optional[float]:
        entry = self._symbols.get(symbol.upper())
        return entry.value if entry else None

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())

    def reset(self, symbol: str) -> None:
        self._symbols.pop(symbol.upper(), None)
