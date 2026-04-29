"""Order flow imbalance tracker: measures buying vs selling pressure from trades."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Optional


@dataclass
class OFIResult:
    symbol: str
    buy_volume: float
    sell_volume: float
    total_volume: float
    ofi: float          # (buy_vol - sell_vol) / total_vol, range [-1, 1]
    trade_count: int

    @property
    def label(self) -> str:
        if self.ofi > 0.4:
            return "Strong Buy"
        if self.ofi > 0.1:
            return "Buy"
        if self.ofi < -0.4:
            return "Strong Sell"
        if self.ofi < -0.1:
            return "Sell"
        return "Neutral"


@dataclass
class _Trade:
    price: float
    volume: float
    side: str  # 'buy' or 'sell'


@dataclass
class SymbolOFI:
    window: int = 100
    _trades: Deque[_Trade] = field(default_factory=deque, init=False, repr=False)

    def record(self, price: float, volume: float, side: str) -> OFIResult:
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")
        if volume < 0:
            raise ValueError(f"volume must be non-negative, got {volume}")
        side = side.lower()
        if side not in ("buy", "sell"):
            raise ValueError(f"side must be 'buy' or 'sell', got {side!r}")
        self._trades.append(_Trade(price, volume, side))
        if len(self._trades) > self.window:
            self._trades.popleft()
        return self._build()

    def _build(self) -> OFIResult:
        buy_vol = sum(t.volume for t in self._trades if t.side == "buy")
        sell_vol = sum(t.volume for t in self._trades if t.side == "sell")
        total = buy_vol + sell_vol
        ofi = (buy_vol - sell_vol) / total if total > 0 else 0.0
        return OFIResult(
            symbol="",
            buy_volume=buy_vol,
            sell_volume=sell_vol,
            total_volume=total,
            ofi=ofi,
            trade_count=len(self._trades),
        )


class OrderFlowImbalanceTracker:
    def __init__(self, window: int = 100, max_symbols: int = 200) -> None:
        if window < 1:
            raise ValueError(f"window must be >= 1, got {window}")
        if max_symbols < 1:
            raise ValueError(f"max_symbols must be >= 1, got {max_symbols}")
        self._window = window
        self._max_symbols = max_symbols
        self._symbols: Dict[str, SymbolOFI] = {}

    def record(self, symbol: str, price: float, volume: float, side: str) -> OFIResult:
        sym = symbol.upper()
        if sym not in self._symbols:
            if len(self._symbols) >= self._max_symbols:
                raise RuntimeError(f"max_symbols limit ({self._max_symbols}) reached")
            self._symbols[sym] = SymbolOFI(window=self._window)
        result = self._symbols[sym].record(price, volume, side)
        result.symbol = sym
        return result

    def get(self, symbol: str) -> Optional[OFIResult]:
        sym = symbol.upper()
        if sym not in self._symbols:
            return None
        return self._symbols[sym]._build()

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
