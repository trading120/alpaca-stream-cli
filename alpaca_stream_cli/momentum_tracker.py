"""Tracks short-term price momentum using rate-of-change (ROC) over a rolling window."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, Dict, Optional


@dataclass
class _Tick:
    price: float
    ts: datetime


@dataclass
class SymbolMomentum:
    """Rolling rate-of-change tracker for a single symbol."""
    window_seconds: float = 60.0
    max_ticks: int = 500
    _ticks: Deque[_Tick] = field(default_factory=deque, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if self.max_ticks < 2:
            raise ValueError("max_ticks must be >= 2")

    def record(self, price: float, ts: datetime) -> None:
        if price <= 0:
            raise ValueError("price must be positive")
        self._ticks.append(_Tick(price=price, ts=ts))
        if len(self._ticks) > self.max_ticks:
            self._ticks.popleft()
        # Prune ticks outside the window
        cutoff = ts.timestamp() - self.window_seconds
        while self._ticks and self._ticks[0].ts.timestamp() < cutoff:
            self._ticks.popleft()

    def roc(self) -> Optional[float]:
        """Return rate-of-change (%) from oldest to newest tick in window."""
        if len(self._ticks) < 2:
            return None
        oldest = self._ticks[0].price
        newest = self._ticks[-1].price
        return (newest - oldest) / oldest * 100.0

    def latest_price(self) -> Optional[float]:
        return self._ticks[-1].price if self._ticks else None

    def tick_count(self) -> int:
        return len(self._ticks)


class MomentumTracker:
    """Multi-symbol momentum tracker."""

    def __init__(self, window_seconds: float = 60.0, max_ticks: int = 500, max_symbols: int = 200) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._window = window_seconds
        self._max_ticks = max_ticks
        self._max_symbols = max_symbols
        self._symbols: Dict[str, SymbolMomentum] = {}

    def record(self, symbol: str, price: float, ts: datetime) -> None:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                raise RuntimeError(f"max_symbols ({self._max_symbols}) reached")
            self._symbols[key] = SymbolMomentum(
                window_seconds=self._window, max_ticks=self._max_ticks
            )
        self._symbols[key].record(price, ts)

    def roc(self, symbol: str) -> Optional[float]:
        return self._symbols.get(symbol.upper(), SymbolMomentum()).roc()

    def get(self, symbol: str) -> Optional[SymbolMomentum]:
        return self._symbols.get(symbol.upper())

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
