"""Support and resistance level tracker based on recent price pivots."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SRResult:
    symbol: str
    support: Optional[float]
    resistance: Optional[float]
    last_price: Optional[float]

    @property
    def near_support(self) -> bool:
        if self.support is None or self.last_price is None:
            return False
        return abs(self.last_price - self.support) / self.last_price < 0.005

    @property
    def near_resistance(self) -> bool:
        if self.resistance is None or self.last_price is None:
            return False
        return abs(self.last_price - self.resistance) / self.last_price < 0.005


@dataclass
class _SymbolSR:
    max_pivots: int = 50
    _prices: deque = field(default_factory=deque)
    _last: Optional[float] = None

    def record(self, price: float) -> None:
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}")
        self._prices.append(price)
        if len(self._prices) > self.max_pivots:
            self._prices.popleft()
        self._last = price

    def support(self) -> Optional[float]:
        if not self._prices:
            return None
        below = [p for p in self._prices if p <= (self._last or float("inf"))]
        return min(below) if below else min(self._prices)

    def resistance(self) -> Optional[float]:
        if not self._prices:
            return None
        above = [p for p in self._prices if p >= (self._last or 0)]
        return max(above) if above else max(self._prices)


class SupportResistanceTracker:
    def __init__(self, max_pivots: int = 50, max_symbols: int = 500) -> None:
        if max_pivots < 2:
            raise ValueError("max_pivots must be >= 2")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max_pivots = max_pivots
        self._max_symbols = max_symbols
        self._symbols: dict[str, _SymbolSR] = {}

    def _get_or_create(self, symbol: str) -> _SymbolSR:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                oldest = next(iter(self._symbols))
                del self._symbols[oldest]
            self._symbols[key] = _SymbolSR(max_pivots=self._max_pivots)
        return self._symbols[key]

    def record(self, symbol: str, price: float) -> SRResult:
        key = symbol.upper()
        tracker = self._get_or_create(key)
        tracker.record(price)
        return SRResult(
            symbol=key,
            support=tracker.support(),
            resistance=tracker.resistance(),
            last_price=price,
        )

    def result(self, symbol: str) -> Optional[SRResult]:
        key = symbol.upper()
        sr = self._symbols.get(key)
        if sr is None or sr._last is None:
            return None
        return SRResult(
            symbol=key,
            support=sr.support(),
            resistance=sr.resistance(),
            last_price=sr._last,
        )

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
