"""Average True Range (ATR) tracker for volatility measurement."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ATRResult:
    symbol: str
    atr: float
    true_range: float
    trade_count: int


def _true_range(high: float, low: float, prev_close: Optional[float]) -> float:
    """Compute the true range for a bar."""
    hl = high - low
    if prev_close is None:
        return hl
    hc = abs(high - prev_close)
    lc = abs(low - prev_close)
    return max(hl, hc, lc)


class SymbolATR:
    """Tracks ATR for a single symbol using Wilder's smoothing."""

    def __init__(self, period: int = 14) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period}")
        self._period = period
        self._trs: deque[float] = deque(maxlen=period)
        self._atr: Optional[float] = None
        self._prev_close: Optional[float] = None
        self._count: int = 0

    def record(self, high: float, low: float, close: float) -> Optional[ATRResult]:
        if high < low:
            raise ValueError("high must be >= low")
        if close < 0:
            raise ValueError("close must be non-negative")
        tr = _true_range(high, low, self._prev_close)
        self._prev_close = close
        self._trs.append(tr)
        self._count += 1
        if len(self._trs) < self._period:
            return None
        if self._atr is None:
            self._atr = sum(self._trs) / self._period
        else:
            self._atr = (self._atr * (self._period - 1) + tr) / self._period
        return ATRResult(
            symbol="", atr=self._atr, true_range=tr, trade_count=self._count
        )

    @property
    def value(self) -> Optional[float]:
        return self._atr

    @property
    def trade_count(self) -> int:
        return self._count


@dataclass
class ATRTracker:
    """Multi-symbol ATR tracker."""

    period: int = 14
    max_symbols: int = 200
    _symbols: dict[str, SymbolATR] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if self.max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {self.max_symbols}")
        if self.period < 1:
            raise ValueError(f"period must be >= 1, got {self.period}")

    def record(self, symbol: str, high: float, low: float, close: float) -> Optional[ATRResult]:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self.max_symbols:
                return None
            self._symbols[key] = SymbolATR(self.period)
        result = self._symbols[key].record(high, low, close)
        if result is not None:
            result.symbol = key
        return result

    def get(self, symbol: str) -> Optional[float]:
        return self._symbols.get(symbol.upper(), SymbolATR(self.period)).value

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
