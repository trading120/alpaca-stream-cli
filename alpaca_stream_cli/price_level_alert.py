"""Tracks whether price has crossed key levels (round numbers, day high/low)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LevelCrossResult:
    symbol: str
    price: float
    level: float
    direction: str  # 'above' or 'below'
    level_type: str  # 'round', 'day_high', 'day_low'

    def __str__(self) -> str:
        return (
            f"{self.symbol} crossed {self.direction} "
            f"{self.level_type} level {self.level:.2f} at {self.price:.2f}"
        )


@dataclass
class _SymbolLevelState:
    prev_price: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None


class PriceLevelAlert:
    """Detects price crossings of round numbers and intraday high/low levels."""

    def __init__(self, round_increments: tuple[float, ...] = (1.0, 5.0, 10.0)) -> None:
        if not round_increments or any(r <= 0 for r in round_increments):
            raise ValueError("round_increments must be non-empty with positive values")
        self._increments = round_increments
        self._states: dict[str, _SymbolLevelState] = {}

    def _get_state(self, symbol: str) -> _SymbolLevelState:
        sym = symbol.upper()
        if sym not in self._states:
            self._states[sym] = _SymbolLevelState()
        return self._states[sym]

    def update_day_range(self, symbol: str, high: float, low: float) -> None:
        """Set the current day high/low for a symbol."""
        if high < low:
            raise ValueError("high must be >= low")
        state = self._get_state(symbol)
        state.day_high = high
        state.day_low = low

    def record(self, symbol: str, price: float) -> list[LevelCrossResult]:
        """Record a new price and return any level crossings detected."""
        if price <= 0:
            raise ValueError("price must be positive")
        sym = symbol.upper()
        state = self._get_state(sym)
        results: list[LevelCrossResult] = []

        if state.prev_price is not None:
            prev = state.prev_price
            results.extend(self._check_round_levels(sym, prev, price))
            results.extend(self._check_day_levels(sym, prev, price, state))

        state.prev_price = price
        if state.day_high is None or price > state.day_high:
            state.day_high = price
        if state.day_low is None or price < state.day_low:
            state.day_low = price

        return results

    def _check_round_levels(
        self, symbol: str, prev: float, current: float
    ) -> list[LevelCrossResult]:
        results = []
        lo, hi = (prev, current) if current >= prev else (current, prev)
        direction = "above" if current >= prev else "below"
        for inc in self._increments:
            first = (int(lo / inc) + 1) * inc
            level = first
            while level <= hi:
                if lo < level <= hi:
                    results.append(
                        LevelCrossResult(symbol, current, round(level, 10), direction, "round")
                    )
                level += inc
        return results

    def _check_day_levels(
        self, symbol: str, prev: float, current: float, state: _SymbolLevelState
    ) -> list[LevelCrossResult]:
        results = []
        if state.day_high is not None and prev < state.day_high <= current:
            results.append(
                LevelCrossResult(symbol, current, state.day_high, "above", "day_high")
            )
        if state.day_low is not None and current <= state.day_low < prev:
            results.append(
                LevelCrossResult(symbol, current, state.day_low, "below", "day_low")
            )
        return results

    def reset(self, symbol: str) -> None:
        self._states.pop(symbol.upper(), None)
