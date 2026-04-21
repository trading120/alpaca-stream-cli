"""Tracks message latency between exchange timestamp and local receipt time."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Dict, Optional


@dataclass
class LatencySample:
    symbol: str
    exchange_ts: datetime
    received_ts: datetime

    @property
    def latency_ms(self) -> float:
        delta = self.received_ts - self.exchange_ts
        return delta.total_seconds() * 1000.0


@dataclass
class SymbolLatency:
    samples: Deque[float] = field(default_factory=lambda: deque(maxlen=50))

    def record(self, latency_ms: float) -> None:
        self.samples.append(latency_ms)

    @property
    def average_ms(self) -> Optional[float]:
        if not self.samples:
            return None
        return sum(self.samples) / len(self.samples)

    @property
    def min_ms(self) -> Optional[float]:
        return min(self.samples) if self.samples else None

    @property
    def max_ms(self) -> Optional[float]:
        return max(self.samples) if self.samples else None

    @property
    def last_ms(self) -> Optional[float]:
        return self.samples[-1] if self.samples else None


class LatencyTracker:
    """Records per-symbol message latency statistics."""

    def __init__(self, max_symbols: int = 500) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max_symbols = max_symbols
        self._data: Dict[str, SymbolLatency] = {}

    def record(self, symbol: str, exchange_ts: datetime) -> float:
        """Record a latency sample using now() as the received timestamp.

        Returns the latency in milliseconds.
        """
        received = datetime.now(tz=timezone.utc)
        symbol = symbol.upper()
        sample = LatencySample(symbol=symbol, exchange_ts=exchange_ts, received_ts=received)
        latency_ms = sample.latency_ms

        if symbol not in self._data:
            if len(self._data) >= self._max_symbols:
                oldest = next(iter(self._data))
                del self._data[oldest]
            self._data[symbol] = SymbolLatency()

        self._data[symbol].record(latency_ms)
        return latency_ms

    def get(self, symbol: str) -> Optional[SymbolLatency]:
        return self._data.get(symbol.upper())

    def symbols(self) -> list[str]:
        return list(self._data.keys())

    def reset(self, symbol: str) -> None:
        self._data.pop(symbol.upper(), None)

    def clear(self) -> None:
        self._data.clear()
