"""Liquidity score tracker combining spread, volume, and trade rate signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LiquidityResult:
    symbol: str
    score: float          # 0.0 (illiquid) to 1.0 (highly liquid)
    spread_component: float
    volume_component: float
    rate_component: float

    @property
    def label(self) -> str:
        if self.score >= 0.75:
            return "HIGH"
        if self.score >= 0.40:
            return "MED"
        return "LOW"


@dataclass
class _SymbolLiquidity:
    spread_norm: float = 1.0   # normalised 0-1 (lower spread → higher score)
    volume_norm: float = 0.0
    rate_norm: float = 0.0

    def score(self) -> float:
        return round(
            0.40 * (1.0 - self.spread_norm)
            + 0.35 * self.volume_norm
            + 0.25 * self.rate_norm,
            4,
        )


class LiquidityScoreTracker:
    """Aggregate spread, volume, and trade-rate signals into a per-symbol
    liquidity score.  All inputs are expected to be pre-normalised to [0, 1].
    """

    def __init__(self, max_symbols: int = 200) -> None:
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._max = max_symbols
        self._data: dict[str, _SymbolLiquidity] = {}

    def _get(self, symbol: str) -> _SymbolLiquidity:
        key = symbol.upper()
        if key not in self._data:
            if len(self._data) >= self._max:
                raise OverflowError(f"Tracking limit of {self._max} symbols reached")
            self._data[key] = _SymbolLiquidity()
        return self._data[key]

    def update_spread(self, symbol: str, spread_norm: float) -> None:
        """spread_norm: 0 = tight (good), 1 = wide (bad)."""
        if not (0.0 <= spread_norm <= 1.0):
            raise ValueError("spread_norm must be in [0, 1]")
        self._get(symbol).spread_norm = spread_norm

    def update_volume(self, symbol: str, volume_norm: float) -> None:
        if not (0.0 <= volume_norm <= 1.0):
            raise ValueError("volume_norm must be in [0, 1]")
        self._get(symbol).volume_norm = volume_norm

    def update_rate(self, symbol: str, rate_norm: float) -> None:
        if not (0.0 <= rate_norm <= 1.0):
            raise ValueError("rate_norm must be in [0, 1]")
        self._get(symbol).rate_norm = rate_norm

    def get(self, symbol: str) -> Optional[LiquidityResult]:
        key = symbol.upper()
        entry = self._data.get(key)
        if entry is None:
            return None
        s = entry.score()
        return LiquidityResult(
            symbol=key,
            score=s,
            spread_component=round(0.40 * (1.0 - entry.spread_norm), 4),
            volume_component=round(0.35 * entry.volume_norm, 4),
            rate_component=round(0.25 * entry.rate_norm, 4),
        )

    def all_results(self) -> list[LiquidityResult]:
        return [r for sym in self._data if (r := self.get(sym)) is not None]
