"""Session-level statistics tracking for symbols during a stream session."""

from dataclasses import dataclass, field
from typing import Dict, Optional
import time


@dataclass
class SymbolStats:
    symbol: str
    session_open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    last: Optional[float] = None
    total_volume: int = 0
    trade_count: int = 0
    session_start_ts: float = field(default_factory=time.time)

    def update(self, price: float, volume: int = 0) -> None:
        if price <= 0:
            return
        if self.session_open is None:
            self.session_open = price
        if self.high is None or price > self.high:
            self.high = price
        if self.low is None or price < self.low:
            self.low = price
        self.last = price
        self.total_volume += volume
        self.trade_count += 1

    @property
    def session_change(self) -> Optional[float]:
        if self.session_open and self.last:
            return self.last - self.session_open
        return None

    @property
    def session_change_pct(self) -> Optional[float]:
        if self.session_open and self.last and self.session_open != 0:
            return (self.last - self.session_open) / self.session_open * 100
        return None


class SessionStats:
    def __init__(self) -> None:
        self._stats: Dict[str, SymbolStats] = {}

    def update(self, symbol: str, price: float, volume: int = 0) -> SymbolStats:
        key = symbol.upper()
        if key not in self._stats:
            self._stats[key] = SymbolStats(symbol=key)
        self._stats[key].update(price, volume)
        return self._stats[key]

    def get(self, symbol: str) -> Optional[SymbolStats]:
        return self._stats.get(symbol.upper())

    def all_symbols(self) -> list:
        return list(self._stats.keys())

    def reset(self, symbol: str) -> None:
        key = symbol.upper()
        if key in self._stats:
            del self._stats[key]

    def reset_all(self) -> None:
        self._stats.clear()
