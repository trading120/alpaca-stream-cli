"""Tracks rolling funding rate estimates based on trade price vs mid-price deviation."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FundingRateResult:
    symbol: str
    rate_pct: float          # estimated funding rate as a percentage
    sample_count: int
    avg_deviation: float     # mean signed deviation of trade price from mid

    @property
    def label(self) -> str:
        if self.rate_pct > 0.05:
            return "bullish"
        if self.rate_pct < -0.05:
            return "bearish"
        return "neutral"


@dataclass
class _SymbolFunding:
    window: int
    _deviations: deque = field(default_factory=deque)

    def record(self, trade_price: float, mid_price: float) -> None:
        if mid_price <= 0:
            return
        dev = (trade_price - mid_price) / mid_price * 100.0
        self._deviations.append(dev)
        while len(self._deviations) > self.window:
            self._deviations.popleft()

    def result(self, symbol: str) -> Optional[FundingRateResult]:
        if not self._deviations:
            return None
        avg = sum(self._deviations) / len(self._deviations)
        return FundingRateResult(
            symbol=symbol,
            rate_pct=avg,
            sample_count=len(self._deviations),
            avg_deviation=avg,
        )


class FundingRateTracker:
    """Tracks funding rate estimates for multiple symbols."""

    def __init__(self, window: int = 100, max_symbols: int = 200) -> None:
        if window < 2:
            raise ValueError("window must be >= 2")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._window = window
        self._max_symbols = max_symbols
        self._symbols: dict[str, _SymbolFunding] = {}

    def record(self, symbol: str, trade_price: float, mid_price: float) -> Optional[FundingRateResult]:
        sym = symbol.upper()
        if sym not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                return None
            self._symbols[sym] = _SymbolFunding(window=self._window)
        self._symbols[sym].record(trade_price, mid_price)
        return self._symbols[sym].result(sym)

    def get(self, symbol: str) -> Optional[FundingRateResult]:
        return self._symbols.get(symbol.upper(), _SymbolFunding(self._window)).result(symbol.upper())

    def all_results(self) -> dict[str, FundingRateResult]:
        out: dict[str, FundingRateResult] = {}
        for sym, tracker in self._symbols.items():
            r = tracker.result(sym)
            if r is not None:
                out[sym] = r
        return out
