"""MACD (Moving Average Convergence Divergence) tracker."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MACDResult:
    macd: float
    signal: float
    histogram: float


@dataclass
class SymbolMACD:
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    _fast_ema: Optional[float] = field(default=None, repr=False)
    _slow_ema: Optional[float] = field(default=None, repr=False)
    _signal_ema: Optional[float] = field(default=None, repr=False)
    _trade_count: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        if self.fast_period < 2:
            raise ValueError("fast_period must be >= 2")
        if self.slow_period <= self.fast_period:
            raise ValueError("slow_period must be > fast_period")
        if self.signal_period < 2:
            raise ValueError("signal_period must be >= 2")

    def _ema_step(self, prev: Optional[float], price: float, period: int) -> float:
        k = 2.0 / (period + 1)
        if prev is None:
            return price
        return price * k + prev * (1.0 - k)

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        self._fast_ema = self._ema_step(self._fast_ema, price, self.fast_period)
        self._slow_ema = self._ema_step(self._slow_ema, price, self.slow_period)
        self._trade_count += 1

        if self._fast_ema is not None and self._slow_ema is not None:
            macd_line = self._fast_ema - self._slow_ema
            self._signal_ema = self._ema_step(self._signal_ema, macd_line, self.signal_period)

    @property
    def value(self) -> Optional[MACDResult]:
        if self._fast_ema is None or self._slow_ema is None or self._signal_ema is None:
            return None
        macd_line = self._fast_ema - self._slow_ema
        signal = self._signal_ema
        return MACDResult(macd=macd_line, signal=signal, histogram=macd_line - signal)

    @property
    def trade_count(self) -> int:
        return self._trade_count


class MACDTracker:
    """Tracks MACD for multiple symbols."""

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        max_symbols: int = 500,
    ) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._fast = fast_period
        self._slow = slow_period
        self._signal = signal_period
        self._max = max_symbols
        self._symbols: dict[str, SymbolMACD] = {}

    def record(self, symbol: str, price: float) -> None:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max:
                return
            self._symbols[key] = SymbolMACD(
                fast_period=self._fast,
                slow_period=self._slow,
                signal_period=self._signal,
            )
        self._symbols[key].record(price)

    def result(self, symbol: str) -> Optional[MACDResult]:
        return self._symbols.get(symbol.upper(), SymbolMACD()).value

    def symbols(self) -> list[str]:
        return sorted(self._symbols.keys())
