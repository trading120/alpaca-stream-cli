"""Volume-Weighted Average Price (VWAP) tracker per symbol."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SymbolVWAP:
    """Accumulates price*volume and total volume to compute VWAP."""

    _cum_pv: float = field(default=0.0, init=False)
    _cum_vol: float = field(default=0.0, init=False)
    _trade_count: int = field(default=0, init=False)

    def record(self, price: float, volume: float) -> None:
        """Record a trade tick."""
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")
        if volume < 0:
            raise ValueError(f"volume must be non-negative, got {volume}")
        self._cum_pv += price * volume
        self._cum_vol += volume
        self._trade_count += 1

    @property
    def value(self) -> Optional[float]:
        """Return current VWAP or None if no volume recorded."""
        if self._cum_vol == 0:
            return None
        return self._cum_pv / self._cum_vol

    @property
    def trade_count(self) -> int:
        return self._trade_count

    def reset(self) -> None:
        """Reset accumulator (e.g. start of new session)."""
        self._cum_pv = 0.0
        self._cum_vol = 0.0
        self._trade_count = 0


class VWAPTracker:
    """Manages per-symbol VWAP accumulators."""

    def __init__(self, max_symbols: int = 200) -> None:
        if max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {max_symbols}")
        self._max = max_symbols
        self._symbols: dict[str, SymbolVWAP] = {}

    def record(self, symbol: str, price: float, volume: float) -> Optional[float]:
        """Record a trade and return the updated VWAP."""
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max:
                return None
            self._symbols[key] = SymbolVWAP()
        self._symbols[key].record(price, volume)
        return self._symbols[key].value

    def get(self, symbol: str) -> Optional[float]:
        """Return current VWAP for a symbol, or None."""
        acc = self._symbols.get(symbol.upper())
        return acc.value if acc else None

    def reset(self, symbol: str) -> None:
        """Reset VWAP for a symbol."""
        acc = self._symbols.get(symbol.upper())
        if acc:
            acc.reset()

    def reset_all(self) -> None:
        """Reset all symbols (e.g. at market open)."""
        for acc in self._symbols.values():
            acc.reset()

    @property
    def tracked_symbols(self) -> list[str]:
        return list(self._symbols.keys())
