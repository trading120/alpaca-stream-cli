"""Bollinger Bands tracker: upper, middle (SMA), and lower bands per symbol."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional
import math


@dataclass
class BollingerResult:
    symbol: str
    upper: float
    middle: float
    lower: float
    bandwidth: float  # (upper - lower) / middle
    price: float

    @property
    def percent_b(self) -> float:
        """Position of price within the band (0 = lower, 1 = upper)."""
        denom = self.upper - self.lower
        if denom == 0.0:
            return 0.5
        return (self.price - self.lower) / denom


class SymbolBollinger:
    def __init__(self, period: int = 20, num_std: float = 2.0) -> None:
        if period < 2:
            raise ValueError("period must be >= 2")
        if num_std <= 0:
            raise ValueError("num_std must be positive")
        self._period = period
        self._num_std = num_std
        self._prices: Deque[float] = deque(maxlen=period)

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        self._prices.append(price)

    def result(self, symbol: str) -> Optional[BollingerResult]:
        if len(self._prices) < self._period:
            return None
        prices = list(self._prices)
        mean = sum(prices) / self._period
        variance = sum((p - mean) ** 2 for p in prices) / self._period
        std = math.sqrt(variance)
        upper = mean + self._num_std * std
        lower = mean - self._num_std * std
        bandwidth = (upper - lower) / mean if mean != 0.0 else 0.0
        return BollingerResult(
            symbol=symbol.upper(),
            upper=upper,
            middle=mean,
            lower=lower,
            bandwidth=bandwidth,
            price=prices[-1],
        )

    @property
    def sample_count(self) -> int:
        return len(self._prices)


class BollingerTracker:
    def __init__(
        self,
        period: int = 20,
        num_std: float = 2.0,
        max_symbols: int = 500,
    ) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._period = period
        self._num_std = num_std
        self._max_symbols = max_symbols
        self._symbols: Dict[str, SymbolBollinger] = {}

    def record(self, symbol: str, price: float) -> Optional[BollingerResult]:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                return None
            self._symbols[key] = SymbolBollinger(self._period, self._num_std)
        self._symbols[key].record(price)
        return self._symbols[key].result(key)

    def get(self, symbol: str) -> Optional[BollingerResult]:
        key = symbol.upper()
        if key not in self._symbols:
            return None
        return self._symbols[key].result(key)

    @property
    def tracked_symbols(self) -> list[str]:
        return list(self._symbols.keys())
