"""Tracks bid/ask size imbalance for symbols to detect buying/selling pressure."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Optional


@dataclass
class ImbalanceSample:
    bid_size: float
    ask_size: float

    @property
    def imbalance(self) -> float:
        """Returns value in [-1.0, 1.0]; positive = buy pressure, negative = sell pressure."""
        total = self.bid_size + self.ask_size
        if total == 0:
            return 0.0
        return (self.bid_size - self.ask_size) / total


class SymbolImbalance:
    """Maintains a rolling window of imbalance samples for a single symbol."""

    def __init__(self, max_samples: int = 50) -> None:
        if max_samples < 1:
            raise ValueError("max_samples must be >= 1")
        self._max_samples = max_samples
        self._samples: deque[ImbalanceSample] = deque(maxlen=max_samples)

    def record(self, bid_size: float, ask_size: float) -> ImbalanceSample:
        sample = ImbalanceSample(bid_size=bid_size, ask_size=ask_size)
        self._samples.append(sample)
        return sample

    def latest_imbalance(self) -> Optional[float]:
        if not self._samples:
            return None
        return self._samples[-1].imbalance

    def average_imbalance(self) -> Optional[float]:
        if not self._samples:
            return None
        return sum(s.imbalance for s in self._samples) / len(self._samples)

    def sample_count(self) -> int:
        return len(self._samples)


class BidAskImbalanceTracker:
    """Tracks bid/ask imbalance across multiple symbols."""

    def __init__(self, max_samples: int = 50, max_symbols: int = 200) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max_samples = max_samples
        self._max_symbols = max_symbols
        self._symbols: dict[str, SymbolImbalance] = {}

    def record(self, symbol: str, bid_size: float, ask_size: float) -> ImbalanceSample:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                raise RuntimeError(f"Max symbol limit ({self._max_symbols}) reached")
            self._symbols[key] = SymbolImbalance(self._max_samples)
        return self._symbols[key].record(bid_size, ask_size)

    def latest_imbalance(self, symbol: str) -> Optional[float]:
        return self._symbols.get(symbol.upper(), SymbolImbalance(1)).latest_imbalance()

    def average_imbalance(self, symbol: str) -> Optional[float]:
        return self._symbols.get(symbol.upper(), SymbolImbalance(1)).average_imbalance()

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
