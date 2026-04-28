"""Tracks a simple sentiment score per symbol derived from trade velocity and price momentum."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SentimentResult:
    symbol: str
    score: float          # -1.0 (very bearish) to +1.0 (very bullish)
    label: str            # "Bullish", "Neutral", "Bearish"
    roc: Optional[float]  # rate-of-change contribution
    trade_rate: Optional[float]  # trades/min contribution


def _label(score: float) -> str:
    if score >= 0.4:
        return "Bullish"
    if score <= -0.4:
        return "Bearish"
    return "Neutral"


class SymbolSentiment:
    """Combines ROC and trade-rate signals into a [-1, 1] sentiment score."""

    def __init__(self, roc_weight: float = 0.6, rate_weight: float = 0.4) -> None:
        if abs(roc_weight + rate_weight - 1.0) > 1e-6:
            raise ValueError("roc_weight + rate_weight must equal 1.0")
        self._roc_w = roc_weight
        self._rate_w = rate_weight
        self._last_roc: Optional[float] = None
        self._last_rate: Optional[float] = None

    def update(self, roc: Optional[float], trade_rate: Optional[float]) -> None:
        self._last_roc = roc
        self._last_rate = trade_rate

    def result(self, symbol: str) -> SentimentResult:
        score = 0.0
        if self._last_roc is not None:
            roc_signal = max(-1.0, min(1.0, self._last_roc / 2.0))
            score += self._roc_w * roc_signal
        if self._last_rate is not None:
            rate_signal = max(-1.0, min(1.0, (self._last_rate - 1.0) / 4.0))
            score += self._rate_w * rate_signal
        score = max(-1.0, min(1.0, score))
        return SentimentResult(
            symbol=symbol.upper(),
            score=round(score, 4),
            label=_label(score),
            roc=self._last_roc,
            trade_rate=self._last_rate,
        )


class SentimentTracker:
    """Manages per-symbol sentiment across all watched symbols."""

    def __init__(self, roc_weight: float = 0.6, rate_weight: float = 0.4) -> None:
        self._rw = roc_weight
        self._tw = rate_weight
        self._symbols: Dict[str, SymbolSentiment] = {}

    def _get(self, symbol: str) -> SymbolSentiment:
        key = symbol.upper()
        if key not in self._symbols:
            self._symbols[key] = SymbolSentiment(self._rw, self._tw)
        return self._symbols[key]

    def update(self, symbol: str, roc: Optional[float], trade_rate: Optional[float]) -> SentimentResult:
        sym = self._get(symbol)
        sym.update(roc, trade_rate)
        return sym.result(symbol)

    def get(self, symbol: str) -> Optional[SentimentResult]:
        key = symbol.upper()
        if key not in self._symbols:
            return None
        return self._symbols[key].result(key)

    def all_results(self) -> Dict[str, SentimentResult]:
        return {k: v.result(k) for k, v in self._symbols.items()}

    def remove(self, symbol: str) -> None:
        self._symbols.pop(symbol.upper(), None)
