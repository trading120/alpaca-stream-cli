"""Tracks whether prices are trading near day high/low bands."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class BandResult:
    symbol: str
    price: float
    day_high: float
    day_low: float
    band_range: float
    pct_from_low: Optional[float]  # 0.0 = at low, 1.0 = at high
    near_high: bool
    near_low: bool


@dataclass
class _SymbolBand:
    day_high: float
    day_low: float
    last_price: float


class PriceBandTracker:
    """Tracks intraday high/low bands and proximity for a set of symbols."""

    def __init__(self, proximity_pct: float = 0.02, max_symbols: int = 500) -> None:
        if proximity_pct < 0:
            raise ValueError("proximity_pct must be non-negative")
        if max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")
        self._proximity_pct = proximity_pct
        self._max_symbols = max_symbols
        self._bands: Dict[str, _SymbolBand] = {}

    def record(self, symbol: str, price: float, day_high: float, day_low: float) -> BandResult:
        if price < 0:
            raise ValueError("price must be non-negative")
        if day_high < day_low:
            raise ValueError("day_high must be >= day_low")
        key = symbol.upper()
        if key not in self._bands and len(self._bands) >= self._max_symbols:
            raise OverflowError(f"max_symbols ({self._max_symbols}) reached")
        self._bands[key] = _SymbolBand(day_high=day_high, day_low=day_low, last_price=price)
        band_range = day_high - day_low
        pct_from_low: Optional[float] = (price - day_low) / band_range if band_range > 0 else None
        threshold = self._proximity_pct
        near_high = (day_high - price) / day_high <= threshold if day_high > 0 else False
        near_low = (price - day_low) / price <= threshold if price > 0 else False
        return BandResult(
            symbol=key,
            price=price,
            day_high=day_high,
            day_low=day_low,
            band_range=band_range,
            pct_from_low=pct_from_low,
            near_high=near_high,
            near_low=near_low,
        )

    def get(self, symbol: str) -> Optional[BandResult]:
        key = symbol.upper()
        band = self._bands.get(key)
        if band is None:
            return None
        return self.record(key, band.last_price, band.day_high, band.day_low)

    def symbols(self) -> list[str]:
        return list(self._bands.keys())

    def remove(self, symbol: str) -> bool:
        return self._bands.pop(symbol.upper(), None) is not None

    def clear(self) -> None:
        self._bands.clear()
