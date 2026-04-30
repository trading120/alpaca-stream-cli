"""Aggregates individual trade ticks into configurable time-based buckets."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class TickBucket:
    """A completed aggregated bucket of ticks for a symbol."""
    symbol: str
    bucket_ts: datetime
    interval_seconds: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: int

    @property
    def change(self) -> float:
        return self.close - self.open

    @property
    def change_pct(self) -> Optional[float]:
        if self.open == 0:
            return None
        return (self.close - self.open) / self.open * 100.0


@dataclass
class _OpenBucket:
    bucket_ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: int


class SymbolAggregator:
    """Aggregates ticks for a single symbol."""

    def __init__(self, symbol: str, interval_seconds: int) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self._symbol = symbol.upper()
        self._interval = interval_seconds
        self._current: Optional[_OpenBucket] = None

    def _bucket_ts(self, ts: datetime) -> datetime:
        epoch = ts.timestamp()
        floored = (epoch // self._interval) * self._interval
        return datetime.fromtimestamp(floored, tz=timezone.utc)

    def record(self, price: float, volume: float, ts: datetime) -> Optional[TickBucket]:
        """Record a tick; returns a completed TickBucket when the bucket rolls."""
        if price <= 0:
            raise ValueError("price must be positive")
        if volume < 0:
            raise ValueError("volume must be non-negative")

        bts = self._bucket_ts(ts)
        completed: Optional[TickBucket] = None

        if self._current is not None and bts != self._current.bucket_ts:
            b = self._current
            completed = TickBucket(
                symbol=self._symbol,
                bucket_ts=b.bucket_ts,
                interval_seconds=self._interval,
                open=b.open, high=b.high, low=b.low, close=b.close,
                volume=b.volume, trade_count=b.trade_count,
            )
            self._current = None

        if self._current is None:
            self._current = _OpenBucket(
                bucket_ts=bts, open=price, high=price,
                low=price, close=price, volume=volume, trade_count=1,
            )
        else:
            b = self._current
            b.high = max(b.high, price)
            b.low = min(b.low, price)
            b.close = price
            b.volume += volume
            b.trade_count += 1

        return completed


class TickAggregator:
    """Multi-symbol tick aggregator."""

    def __init__(self, interval_seconds: int = 60, max_symbols: int = 500) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        if max_symbols <= 0:
            raise ValueError("max_symbols must be positive")
        self._interval = interval_seconds
        self._max = max_symbols
        self._aggs: Dict[str, SymbolAggregator] = {}
        self._completed: Dict[str, List[TickBucket]] = {}

    def record(self, symbol: str, price: float, volume: float, ts: datetime) -> Optional[TickBucket]:
        sym = symbol.upper()
        if sym not in self._aggs:
            if len(self._aggs) >= self._max:
                return None
            self._aggs[sym] = SymbolAggregator(sym, self._interval)
            self._completed[sym] = []
        bucket = self._aggs[sym].record(price, volume, ts)
        if bucket is not None:
            self._completed[sym].append(bucket)
        return bucket

    def completed(self, symbol: str) -> List[TickBucket]:
        return list(self._completed.get(symbol.upper(), []))

    def symbols(self) -> List[str]:
        return list(self._aggs.keys())
