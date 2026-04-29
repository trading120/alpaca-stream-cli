"""Classic pivot point calculator (floor trader method)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass(frozen=True)
class PivotResult:
    symbol: str
    pivot: float
    r1: float
    r2: float
    r3: float
    s1: float
    s2: float
    s3: float

    def nearest_level(self, price: float) -> tuple[str, float]:
        """Return (label, level) of the level closest to *price*."""
        levels = {
            "P": self.pivot,
            "R1": self.r1, "R2": self.r2, "R3": self.r3,
            "S1": self.s1, "S2": self.s2, "S3": self.s3,
        }
        return min(levels.items(), key=lambda kv: abs(kv[1] - price))


def _calc(high: float, low: float, close: float) -> PivotResult:
    pivot = (high + low + close) / 3.0
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)
    return PivotResult(
        symbol="",
        pivot=round(pivot, 4),
        r1=round(r1, 4), r2=round(r2, 4), r3=round(r3, 4),
        s1=round(s1, 4), s2=round(s2, 4), s3=round(s3, 4),
    )


@dataclass
class PivotPointTracker:
    max_symbols: int = 200
    _store: Dict[str, PivotResult] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.max_symbols < 1:
            raise ValueError("max_symbols must be >= 1")

    def update(self, symbol: str, high: float, low: float, close: float) -> PivotResult:
        """Compute and store pivot points for *symbol* from prior-bar HLC."""
        if high < low:
            raise ValueError("high must be >= low")
        if close < 0 or high < 0 or low < 0:
            raise ValueError("prices must be non-negative")
        key = symbol.upper()
        if key not in self._store and len(self._store) >= self.max_symbols:
            raise OverflowError(f"tracker is full ({self.max_symbols} symbols)")
        raw = _calc(high, low, close)
        result = PivotResult(
            symbol=key,
            pivot=raw.pivot,
            r1=raw.r1, r2=raw.r2, r3=raw.r3,
            s1=raw.s1, s2=raw.s2, s3=raw.s3,
        )
        self._store[key] = result
        return result

    def get(self, symbol: str) -> Optional[PivotResult]:
        return self._store.get(symbol.upper())

    def all_symbols(self) -> list[str]:
        return list(self._store.keys())

    def remove(self, symbol: str) -> None:
        self._store.pop(symbol.upper(), None)

    def clear(self) -> None:
        self._store.clear()
