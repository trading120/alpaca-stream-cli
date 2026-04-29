"""Tracks rolling price correlation between symbol pairs."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Tuple
import math

_DEFAULT_WINDOW = 20
_DEFAULT_MAX_SYMBOLS = 50


@dataclass
class CorrelationResult:
    symbol_a: str
    symbol_b: str
    correlation: Optional[float]  # -1.0 to 1.0
    sample_count: int


class _SymbolBuffer:
    def __init__(self, window: int) -> None:
        self._prices: Deque[float] = deque(maxlen=window)

    def record(self, price: float) -> None:
        if price < 0:
            raise ValueError(f"Price must be non-negative, got {price}")
        self._prices.append(price)

    def values(self) -> list:
        return list(self._prices)

    def __len__(self) -> int:
        return len(self._prices)


def _pearson(xs: list, ys: list) -> Optional[float]:
    n = len(xs)
    if n < 2 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return max(-1.0, min(1.0, num / (dx * dy)))


class CorrelationTracker:
    def __init__(self, window: int = _DEFAULT_WINDOW, max_symbols: int = _DEFAULT_MAX_SYMBOLS) -> None:
        if window < 2:
            raise ValueError(f"window must be >= 2, got {window}")
        if max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {max_symbols}")
        self._window = window
        self._max_symbols = max_symbols
        self._buffers: Dict[str, _SymbolBuffer] = {}

    def record(self, symbol: str, price: float) -> None:
        key = symbol.upper()
        if key not in self._buffers:
            if len(self._buffers) >= self._max_symbols:
                return
            self._buffers[key] = _SymbolBuffer(self._window)
        self._buffers[key].record(price)

    def correlation(self, symbol_a: str, symbol_b: str) -> CorrelationResult:
        a, b = symbol_a.upper(), symbol_b.upper()
        buf_a = self._buffers.get(a)
        buf_b = self._buffers.get(b)
        if buf_a is None or buf_b is None:
            return CorrelationResult(a, b, None, 0)
        xs, ys = buf_a.values(), buf_b.values()
        n = min(len(xs), len(ys))
        xs, ys = xs[-n:], ys[-n:]
        corr = _pearson(xs, ys)
        return CorrelationResult(a, b, corr, n)

    def symbols(self) -> list:
        return sorted(self._buffers.keys())

    def pairs(self) -> list:
        syms = self.symbols()
        return [(syms[i], syms[j]) for i in range(len(syms)) for j in range(i + 1, len(syms))]
