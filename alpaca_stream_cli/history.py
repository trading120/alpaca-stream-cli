"""Price history tracking for symbols in the watchlist."""
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional
import time


MAX_HISTORY_POINTS = 100


@dataclass
class PricePoint:
    price: float
    timestamp: float = field(default_factory=time.time)


class PriceHistory:
    """Maintains a rolling window of price points per symbol."""

    def __init__(self, max_points: int = MAX_HISTORY_POINTS) -> None:
        self.max_points = max_points
        self._history: Dict[str, Deque[PricePoint]] = {}

    def record(self, symbol: str, price: float) -> None:
        """Record a new price point for the given symbol."""
        symbol = symbol.upper()
        if symbol not in self._history:
            self._history[symbol] = deque(maxlen=self.max_points)
        self._history[symbol].append(PricePoint(price=price))

    def get(self, symbol: str) -> list[PricePoint]:
        """Return the list of recorded price points for a symbol."""
        return list(self._history.get(symbol.upper(), []))

    def latest(self, symbol: str) -> Optional[PricePoint]:
        """Return the most recent price point for a symbol, or None."""
        points = self._history.get(symbol.upper())
        if not points:
            return None
        return points[-1]

    def change_pct(self, symbol: str) -> Optional[float]:
        """Return percentage change from first to last recorded price."""
        points = self._history.get(symbol.upper())
        if not points or len(points) < 2:
            return None
        first = points[0].price
        last = points[-1].price
        if first == 0:
            return None
        return ((last - first) / first) * 100

    def clear(self, symbol: str) -> None:
        """Clear history for a specific symbol."""
        self._history.pop(symbol.upper(), None)

    def clear_all(self) -> None:
        """Clear all recorded history."""
        self._history.clear()

    @property
    def tracked_symbols(self) -> list[str]:
        """Return list of symbols currently being tracked."""
        return list(self._history.keys())
