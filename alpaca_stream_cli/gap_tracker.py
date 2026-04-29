"""Tracks overnight/intraday price gaps for symbols."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class GapResult:
    symbol: str
    prev_close: float
    open_price: float
    gap: float          # absolute gap
    gap_pct: float      # percentage gap
    filled: bool = False  # True once price returns to prev_close side

    @property
    def is_gap_up(self) -> bool:
        return self.gap > 0

    @property
    def is_gap_down(self) -> bool:
        return self.gap < 0


@dataclass
class _SymbolGap:
    prev_close: Optional[float] = None
    result: Optional[GapResult] = None


class GapTracker:
    """Records previous close and open price to compute gap metrics."""

    def __init__(self, max_symbols: int = 200) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max = max_symbols
        self._data: Dict[str, _SymbolGap] = {}

    def set_prev_close(self, symbol: str, price: float) -> None:
        """Record the previous session's closing price."""
        if price < 0:
            raise ValueError("price must be non-negative")
        key = symbol.upper()
        if key not in self._data:
            if len(self._data) >= self._max:
                return
            self._data[key] = _SymbolGap()
        self._data[key].prev_close = price
        self._data[key].result = None  # reset on new close

    def record_open(self, symbol: str, open_price: float) -> Optional[GapResult]:
        """Record the opening price and compute the gap."""
        if open_price < 0:
            raise ValueError("open_price must be non-negative")
        key = symbol.upper()
        entry = self._data.get(key)
        if entry is None or entry.prev_close is None:
            return None
        gap = open_price - entry.prev_close
        gap_pct = (gap / entry.prev_close * 100) if entry.prev_close != 0 else 0.0
        result = GapResult(
            symbol=key,
            prev_close=entry.prev_close,
            open_price=open_price,
            gap=gap,
            gap_pct=gap_pct,
        )
        entry.result = result
        return result

    def check_fill(self, symbol: str, current_price: float) -> bool:
        """Mark gap as filled if price crosses back through prev_close."""
        key = symbol.upper()
        entry = self._data.get(key)
        if entry is None or entry.result is None:
            return False
        r = entry.result
        if r.filled:
            return True
        if r.is_gap_up and current_price <= r.prev_close:
            r.filled = True
        elif r.is_gap_down and current_price >= r.prev_close:
            r.filled = True
        return r.filled

    def get(self, symbol: str) -> Optional[GapResult]:
        entry = self._data.get(symbol.upper())
        return entry.result if entry else None

    def all_results(self) -> Dict[str, GapResult]:
        return {
            sym: e.result
            for sym, e in self._data.items()
            if e.result is not None
        }
