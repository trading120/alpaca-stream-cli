"""Tracks bid/ask spread statistics per symbol over a rolling window."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, Dict, Optional


@dataclass
class _SpreadSample:
    bid: float
    ask: float
    ts: datetime

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread_pct(self) -> Optional[float]:
        if self.mid == 0:
            return None
        return (self.spread / self.mid) * 100.0


class SymbolSpreadTracker:
    """Rolling spread tracker for a single symbol."""

    def __init__(self, max_samples: int = 100) -> None:
        if max_samples < 1:
            raise ValueError("max_samples must be >= 1")
        self._max = max_samples
        self._samples: Deque[_SpreadSample] = deque()

    def record(self, bid: float, ask: float, ts: Optional[datetime] = None) -> _SpreadSample:
        sample = _SpreadSample(bid=bid, ask=ask, ts=ts or datetime.utcnow())
        self._samples.append(sample)
        if len(self._samples) > self._max:
            self._samples.popleft()
        return sample

    def latest(self) -> Optional[_SpreadSample]:
        return self._samples[-1] if self._samples else None

    def average_spread(self) -> Optional[float]:
        if not self._samples:
            return None
        return sum(s.spread for s in self._samples) / len(self._samples)

    def average_spread_pct(self) -> Optional[float]:
        pcts = [s.spread_pct for s in self._samples if s.spread_pct is not None]
        if not pcts:
            return None
        return sum(pcts) / len(pcts)

    def __len__(self) -> int:
        return len(self._samples)


@dataclass
class QuoteSpreadTracker:
    """Multi-symbol spread tracker."""

    max_samples: int = 100
    _trackers: Dict[str, SymbolSpreadTracker] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_samples < 1:
            raise ValueError("max_samples must be >= 1")

    def record(self, symbol: str, bid: float, ask: float, ts: Optional[datetime] = None) -> _SpreadSample:
        key = symbol.upper()
        if key not in self._trackers:
            self._trackers[key] = SymbolSpreadTracker(self.max_samples)
        return self._trackers[key].record(bid, ask, ts)

    def get(self, symbol: str) -> Optional[SymbolSpreadTracker]:
        return self._trackers.get(symbol.upper())

    def symbols(self) -> list[str]:
        return sorted(self._trackers.keys())

    def remove(self, symbol: str) -> None:
        self._trackers.pop(symbol.upper(), None)

    def clear(self) -> None:
        self._trackers.clear()
