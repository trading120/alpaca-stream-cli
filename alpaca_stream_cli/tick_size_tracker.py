"""Tracks minimum observed tick size (price increment) per symbol."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SymbolTickSize:
    """Accumulates price observations and derives the minimum tick size."""

    _prices: List[float] = field(default_factory=list, repr=False)
    _min_tick: Optional[float] = None

    def record(self, price: float) -> None:
        """Record a new price observation and update the minimum tick size."""
        if price <= 0:
            raise ValueError(f"Price must be positive, got {price}")
        if self._prices:
            diff = abs(price - self._prices[-1])
            if diff > 0:
                rounded = round(diff, 6)
                if self._min_tick is None or rounded < self._min_tick:
                    self._min_tick = rounded
        self._prices.append(price)

    @property
    def min_tick(self) -> Optional[float]:
        """Return the minimum observed tick size, or None if fewer than 2 prices."""
        return self._min_tick

    @property
    def sample_count(self) -> int:
        return len(self._prices)


class TickSizeTracker:
    """Manages per-symbol tick size tracking across multiple symbols."""

    def __init__(self, max_symbols: int = 500) -> None:
        if max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {max_symbols}")
        self._max_symbols = max_symbols
        self._symbols: Dict[str, SymbolTickSize] = {}

    def record(self, symbol: str, price: float) -> Optional[float]:
        """Record a price for a symbol; returns updated min tick or None."""
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                return None
            self._symbols[key] = SymbolTickSize()
        self._symbols[key].record(price)
        return self._symbols[key].min_tick

    def min_tick(self, symbol: str) -> Optional[float]:
        """Return the minimum tick size for *symbol*, or None if unknown."""
        entry = self._symbols.get(symbol.upper())
        return entry.min_tick if entry else None

    def sample_count(self, symbol: str) -> int:
        """Return the number of price samples recorded for *symbol*."""
        entry = self._symbols.get(symbol.upper())
        return entry.sample_count if entry else 0

    def known_symbols(self) -> List[str]:
        """Return sorted list of tracked symbols."""
        return sorted(self._symbols.keys())

    def remove(self, symbol: str) -> bool:
        """Remove a symbol from tracking; returns True if it existed."""
        return self._symbols.pop(symbol.upper(), None) is not None
