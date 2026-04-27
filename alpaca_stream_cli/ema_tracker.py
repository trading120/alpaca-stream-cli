"""Exponential Moving Average (EMA) tracker per symbol."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SymbolEMA:
    """Tracks EMA for a single symbol."""

    period: int
    _value: Optional[float] = field(default=None, init=False, repr=False)
    _sample_count: int = field(default=0, init=False, repr=False)
    _k: float = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.period < 2:
            raise ValueError("period must be >= 2")
        self._k = 2.0 / (self.period + 1)

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError("price must be non-negative")
        self._sample_count += 1
        if self._value is None:
            self._value = price
        else:
            self._value = price * self._k + self._value * (1.0 - self._k)

    @property
    def value(self) -> Optional[float]:
        """Current EMA value, or None if no records yet."""
        return self._value

    @property
    def sample_count(self) -> int:
        return self._sample_count

    def reset(self) -> None:
        self._value = None
        self._sample_count = 0


class EMATracker:
    """Manages per-symbol EMA with a shared period."""

    def __init__(self, period: int = 20, max_symbols: int = 500) -> None:
        if period < 2:
            raise ValueError("period must be >= 2")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._period = period
        self._max_symbols = max_symbols
        self._symbols: Dict[str, SymbolEMA] = {}

    def record(self, symbol: str, price: float) -> Optional[float]:
        """Record a price for *symbol* and return the updated EMA value."""
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                raise RuntimeError("max_symbols limit reached")
            self._symbols[key] = SymbolEMA(period=self._period)
        self._symbols[key].record(price)
        return self._symbols[key].value

    def value(self, symbol: str) -> Optional[float]:
        entry = self._symbols.get(symbol.upper())
        return entry.value if entry else None

    def sample_count(self, symbol: str) -> int:
        entry = self._symbols.get(symbol.upper())
        return entry.sample_count if entry else 0

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())

    def reset(self, symbol: str) -> None:
        entry = self._symbols.get(symbol.upper())
        if entry:
            entry.reset()
