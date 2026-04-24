"""Tracks trades-per-second (TPS) rate for symbols over a rolling window."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, Optional


@dataclass
class _Stamp:
    ts: datetime


@dataclass
class SymbolTradeRate:
    """Rolling-window trade rate tracker for a single symbol."""
    window_seconds: float = 10.0
    _stamps: Deque[_Stamp] = field(default_factory=deque, init=False, repr=False)

    def record(self, ts: Optional[datetime] = None) -> None:
        """Record a trade event at the given timestamp (default: now)."""
        if ts is None:
            ts = datetime.now(tz=timezone.utc)
        self._stamps.append(_Stamp(ts=ts))
        self._evict(ts)

    def rate(self, now: Optional[datetime] = None) -> float:
        """Return trades per second over the rolling window."""
        if now is None:
            now = datetime.now(tz=timezone.utc)
        self._evict(now)
        if not self._stamps:
            return 0.0
        return len(self._stamps) / self.window_seconds

    def count(self, now: Optional[datetime] = None) -> int:
        """Return raw trade count within the rolling window."""
        if now is None:
            now = datetime.now(tz=timezone.utc)
        self._evict(now)
        return len(self._stamps)

    def _evict(self, now: datetime) -> None:
        cutoff = now.timestamp() - self.window_seconds
        while self._stamps and self._stamps[0].ts.timestamp() < cutoff:
            self._stamps.popleft()


class TradeRateTracker:
    """Manages per-symbol rolling trade rate across the session."""

    def __init__(self, window_seconds: float = 10.0, max_symbols: int = 500) -> None:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        if max_symbols < 1:
            raise ValueError("max_symbols must be at least 1")
        self._window = window_seconds
        self._max = max_symbols
        self._trackers: Dict[str, SymbolTradeRate] = {}

    def record(self, symbol: str, ts: Optional[datetime] = None) -> None:
        key = symbol.upper()
        if key not in self._trackers:
            if len(self._trackers) >= self._max:
                return
            self._trackers[key] = SymbolTradeRate(window_seconds=self._window)
        self._trackers[key].record(ts)

    def rate(self, symbol: str, now: Optional[datetime] = None) -> float:
        tracker = self._trackers.get(symbol.upper())
        return tracker.rate(now) if tracker else 0.0

    def count(self, symbol: str, now: Optional[datetime] = None) -> int:
        tracker = self._trackers.get(symbol.upper())
        return tracker.count(now) if tracker else 0

    def all_rates(self, now: Optional[datetime] = None) -> Dict[str, float]:
        return {sym: t.rate(now) for sym, t in self._trackers.items()}

    def symbols(self) -> list[str]:
        return sorted(self._trackers.keys())
