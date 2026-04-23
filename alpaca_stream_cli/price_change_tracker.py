"""Tracks intra-session price change velocity for symbols."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, Optional


@dataclass
class _Tick:
    price: float
    ts: datetime


@dataclass
class SymbolVelocity:
    """Rolling price-change velocity for a single symbol."""
    symbol: str
    _ticks: Deque[_Tick] = field(default_factory=lambda: deque(maxlen=60), repr=False)

    def record(self, price: float, ts: Optional[datetime] = None) -> None:
        """Record a new price tick."""
        if ts is None:
            ts = datetime.now(timezone.utc)
        self._ticks.append(_Tick(price=price, ts=ts))

    def change_over_window(self, seconds: float) -> Optional[float]:
        """Return absolute price change over the last *seconds* window.

        Returns ``None`` if fewer than two ticks exist in the window.
        """
        if len(self._ticks) < 2:
            return None
        now = self._ticks[-1].ts
        cutoff = now.timestamp() - seconds
        in_window = [t for t in self._ticks if t.ts.timestamp() >= cutoff]
        if len(in_window) < 2:
            return None
        return in_window[-1].price - in_window[0].price

    def pct_change_over_window(self, seconds: float) -> Optional[float]:
        """Return percentage price change over the last *seconds* window."""
        if len(self._ticks) < 2:
            return None
        now = self._ticks[-1].ts
        cutoff = now.timestamp() - seconds
        in_window = [t for t in self._ticks if t.ts.timestamp() >= cutoff]
        if len(in_window) < 2:
            return None
        base = in_window[0].price
        if base == 0:
            return None
        return (in_window[-1].price - base) / base * 100.0

    @property
    def latest_price(self) -> Optional[float]:
        """Most recently recorded price, or ``None``."""
        return self._ticks[-1].price if self._ticks else None


class PriceChangeTracker:
    """Manages per-symbol velocity tracking."""

    def __init__(self, max_ticks_per_symbol: int = 60) -> None:
        if max_ticks_per_symbol < 1:
            raise ValueError("max_ticks_per_symbol must be >= 1")
        self._max = max_ticks_per_symbol
        self._symbols: Dict[str, SymbolVelocity] = {}

    def record(self, symbol: str, price: float, ts: Optional[datetime] = None) -> None:
        """Record a price tick for *symbol*."""
        key = symbol.upper()
        if key not in self._symbols:
            sv = SymbolVelocity(symbol=key)
            sv._ticks = deque(maxlen=self._max)
            self._symbols[key] = sv
        self._symbols[key].record(price, ts)

    def get(self, symbol: str) -> Optional[SymbolVelocity]:
        """Return the :class:`SymbolVelocity` for *symbol*, or ``None``."""
        return self._symbols.get(symbol.upper())

    def symbols(self) -> list[str]:
        """Return sorted list of tracked symbols."""
        return sorted(self._symbols.keys())

    def remove(self, symbol: str) -> bool:
        """Remove tracking for *symbol*. Returns ``True`` if it existed."""
        return self._symbols.pop(symbol.upper(), None) is not None
