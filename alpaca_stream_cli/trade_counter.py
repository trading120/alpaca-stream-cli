"""Tracks per-symbol trade counts over a rolling time window."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, Optional


@dataclass
class _Stamp:
    ts: datetime


class SymbolTradeCounter:
    """Maintains a rolling window of trade timestamps for one symbol."""

    def __init__(self, window_seconds: float = 60.0) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._window = window_seconds
        self._stamps: Deque[datetime] = deque()

    def record(self, ts: Optional[datetime] = None) -> int:
        """Record a trade and return the current count within the window."""
        now = ts or datetime.now(timezone.utc)
        self._stamps.append(now)
        self._evict(now)
        return len(self._stamps)

    def count(self, as_of: Optional[datetime] = None) -> int:
        """Return how many trades occurred within the rolling window."""
        now = as_of or datetime.now(timezone.utc)
        self._evict(now)
        return len(self._stamps)

    def reset(self) -> None:
        self._stamps.clear()

    def _evict(self, now: datetime) -> None:
        cutoff = now.timestamp() - self._window
        while self._stamps and self._stamps[0].timestamp() < cutoff:
            self._stamps.popleft()


class TradeCounter:
    """Aggregates per-symbol rolling trade counts."""

    def __init__(self, window_seconds: float = 60.0, max_symbols: int = 500) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if max_symbols < 1:
            raise ValueError("max_symbols must be at least 1")
        self._window = window_seconds
        self._max_symbols = max_symbols
        self._counters: Dict[str, SymbolTradeCounter] = {}

    def record(self, symbol: str, ts: Optional[datetime] = None) -> int:
        """Record a trade for *symbol*; returns updated rolling count."""
        key = symbol.upper()
        if key not in self._counters:
            if len(self._counters) >= self._max_symbols:
                raise OverflowError(f"max_symbols ({self._max_symbols}) reached")
            self._counters[key] = SymbolTradeCounter(self._window)
        return self._counters[key].record(ts)

    def count(self, symbol: str, as_of: Optional[datetime] = None) -> int:
        """Return rolling trade count for *symbol* (0 if never seen)."""
        key = symbol.upper()
        if key not in self._counters:
            return 0
        return self._counters[key].count(as_of)

    def all_counts(self, as_of: Optional[datetime] = None) -> Dict[str, int]:
        """Return a dict of symbol -> rolling count for all tracked symbols."""
        return {sym: ctr.count(as_of) for sym, ctr in self._counters.items()}

    def reset(self, symbol: Optional[str] = None) -> None:
        """Reset one symbol or all symbols if *symbol* is None."""
        if symbol is not None:
            key = symbol.upper()
            if key in self._counters:
                self._counters[key].reset()
        else:
            for ctr in self._counters.values():
                ctr.reset()
