"""Stochastic Oscillator (%K and %D) tracker per symbol."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StochasticResult:
    k: float  # %K line
    d: float  # %D line (SMA of %K)

    @property
    def is_overbought(self) -> bool:
        return self.k >= 80.0

    @property
    def is_oversold(self) -> bool:
        return self.k <= 20.0


@dataclass
class SymbolStochastic:
    k_period: int = 14
    d_period: int = 3
    _prices: deque = field(default_factory=deque, init=False, repr=False)
    _k_values: deque = field(default_factory=deque, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.k_period < 2:
            raise ValueError("k_period must be >= 2")
        if self.d_period < 1:
            raise ValueError("d_period must be >= 1")
        self._prices = deque(maxlen=self.k_period)
        self._k_values = deque(maxlen=self.d_period)

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        self._prices.append(price)
        if len(self._prices) == self.k_period:
            lo = min(self._prices)
            hi = max(self._prices)
            k = 100.0 * (price - lo) / (hi - lo) if hi != lo else 50.0
            self._k_values.append(k)

    @property
    def value(self) -> Optional[StochasticResult]:
        if len(self._k_values) < self.d_period:
            return None
        d = sum(self._k_values) / len(self._k_values)
        return StochasticResult(k=self._k_values[-1], d=d)

    @property
    def sample_count(self) -> int:
        return len(self._prices)


class StochasticTracker:
    """Tracks stochastic oscillator for multiple symbols."""

    def __init__(
        self,
        k_period: int = 14,
        d_period: int = 3,
        max_symbols: int = 500,
    ) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._k_period = k_period
        self._d_period = d_period
        self._max_symbols = max_symbols
        self._symbols: dict[str, SymbolStochastic] = {}

    def record(self, symbol: str, price: float) -> None:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                raise RuntimeError("max_symbols limit reached")
            self._symbols[key] = SymbolStochastic(
                k_period=self._k_period, d_period=self._d_period
            )
        self._symbols[key].record(price)

    def result(self, symbol: str) -> Optional[StochasticResult]:
        sym = self._symbols.get(symbol.upper())
        return sym.value if sym else None

    @property
    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
