"""Tracks price breakouts above resistance or below support over a rolling window."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Optional


@dataclass
class BreakoutResult:
    symbol: str
    price: float
    upper: float
    lower: float
    breakout_up: bool
    breakout_down: bool
    pct_above_upper: Optional[float]
    pct_below_lower: Optional[float]

    def __str__(self) -> str:
        if self.breakout_up:
            return f"{self.symbol} broke out UP above {self.upper:.2f} (+{self.pct_above_upper:.2f}%)"
        if self.breakout_down:
            return f"{self.symbol} broke out DOWN below {self.lower:.2f} ({self.pct_below_lower:.2f}%)"
        return f"{self.symbol} within range [{self.lower:.2f}, {self.upper:.2f}]"


@dataclass
class _SymbolBreakout:
    window: int
    prices: deque = field(default_factory=deque)

    def record(self, price: float) -> BreakoutResult:
        if price < 0:
            raise ValueError("price must be non-negative")
        self.prices.append(price)
        if len(self.prices) > self.window:
            self.prices.popleft()
        upper = max(self.prices)
        lower = min(self.prices)
        breakout_up = price >= upper and len(self.prices) == self.window and price > self.prices[-2] if len(self.prices) > 1 else False
        breakout_down = price <= lower and len(self.prices) == self.window and price < self.prices[-2] if len(self.prices) > 1 else False
        pct_above = ((price - upper) / upper * 100) if breakout_up and upper else None
        pct_below = ((price - lower) / lower * 100) if breakout_down and lower else None
        return BreakoutResult(
            symbol="",
            price=price,
            upper=upper,
            lower=lower,
            breakout_up=breakout_up,
            breakout_down=breakout_down,
            pct_above_upper=pct_above,
            pct_below_lower=pct_below,
        )


class BreakoutTracker:
    def __init__(self, window: int = 20, max_symbols: int = 200) -> None:
        if window < 2:
            raise ValueError("window must be >= 2")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._window = window
        self._max = max_symbols
        self._symbols: dict[str, _SymbolBreakout] = {}

    def record(self, symbol: str, price: float) -> BreakoutResult:
        key = symbol.upper()
        if key not in self._symbols:
            if len(self._symbols) >= self._max:
                raise RuntimeError("max_symbols limit reached")
            self._symbols[key] = _SymbolBreakout(window=self._window)
        result = self._symbols[key].record(price)
        result.symbol = key
        return result

    def get(self, symbol: str) -> Optional[BreakoutResult]:
        key = symbol.upper()
        if key not in self._symbols or not self._symbols[key].prices:
            return None
        return self._symbols[key].record(list(self._symbols[key].prices)[-1])

    def symbols(self) -> list[str]:
        return list(self._symbols.keys())
