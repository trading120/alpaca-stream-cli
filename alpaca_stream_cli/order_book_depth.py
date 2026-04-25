"""Tracks top-of-book bid/ask depth levels for symbols."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DepthLevel:
    price: float
    size: float


@dataclass
class BookSnapshot:
    symbol: str
    bids: List[DepthLevel] = field(default_factory=list)
    asks: List[DepthLevel] = field(default_factory=list)

    @property
    def best_bid(self) -> Optional[DepthLevel]:
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> Optional[DepthLevel]:
        return self.asks[0] if self.asks else None

    @property
    def total_bid_size(self) -> float:
        return sum(l.size for l in self.bids)

    @property
    def total_ask_size(self) -> float:
        return sum(l.size for l in self.asks)


class OrderBookDepth:
    """Maintains per-symbol order book depth snapshots."""

    def __init__(self, max_levels: int = 5, max_symbols: int = 100) -> None:
        if max_levels < 1:
            raise ValueError("max_levels must be >= 1")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max_levels = max_levels
        self._max_symbols = max_symbols
        self._books: dict[str, BookSnapshot] = {}

    def update(self, symbol: str, bids: List[tuple], asks: List[tuple]) -> BookSnapshot:
        """Update depth for a symbol. bids/asks are lists of (price, size) tuples."""
        key = symbol.upper()
        if key not in self._books:
            if len(self._books) >= self._max_symbols:
                return self._books.get(key, BookSnapshot(symbol=key))
            self._books[key] = BookSnapshot(symbol=key)
        snap = self._books[key]
        snap.bids = [DepthLevel(price=p, size=s) for p, s in bids[: self._max_levels]]
        snap.asks = [DepthLevel(price=p, size=s) for p, s in asks[: self._max_levels]]
        return snap

    def get(self, symbol: str) -> Optional[BookSnapshot]:
        return self._books.get(symbol.upper())

    def remove(self, symbol: str) -> bool:
        return self._books.pop(symbol.upper(), None) is not None

    def symbols(self) -> List[str]:
        return list(self._books.keys())

    def clear(self) -> None:
        self._books.clear()
