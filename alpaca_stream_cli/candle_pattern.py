"""Candlestick pattern detector for OHLCV bars."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from alpaca_stream_cli.ohlcv_bar import OHLCVBar


@dataclass(frozen=True)
class PatternResult:
    symbol: str
    pattern: Optional[str]  # None if no pattern detected
    bullish: Optional[bool]  # True=bullish, False=bearish, None=neutral/unknown

    def __str__(self) -> str:
        if self.pattern is None:
            return f"{self.symbol}: no pattern"
        direction = "bullish" if self.bullish else ("bearish" if self.bullish is False else "neutral")
        return f"{self.symbol}: {self.pattern} ({direction})"


def _body(bar: OHLCVBar) -> float:
    return abs(bar.close - bar.open)


def _range(bar: OHLCVBar) -> float:
    return bar.high - bar.low if bar.high > bar.low else 0.0


def detect_pattern(bar: OHLCVBar) -> PatternResult:
    """Detect a simple single-bar candlestick pattern."""
    body = _body(bar)
    rng = _range(bar)
    if rng == 0:
        return PatternResult(symbol=bar.symbol, pattern=None, bullish=None)

    body_ratio = body / rng
    upper_wick = bar.high - max(bar.open, bar.close)
    lower_wick = min(bar.open, bar.close) - bar.low
    is_bullish_candle = bar.close >= bar.open

    # Doji: tiny body
    if body_ratio < 0.1:
        return PatternResult(symbol=bar.symbol, pattern="doji", bullish=None)

    # Hammer: small body at top, long lower wick, bullish signal
    if lower_wick >= 2 * body and upper_wick <= 0.1 * rng and not is_bullish_candle is False:
        return PatternResult(symbol=bar.symbol, pattern="hammer", bullish=True)

    # Shooting star: small body at bottom, long upper wick, bearish signal
    if upper_wick >= 2 * body and lower_wick <= 0.1 * rng:
        return PatternResult(symbol=bar.symbol, pattern="shooting_star", bullish=False)

    # Marubozu: full body candle, almost no wicks
    if body_ratio >= 0.9:
        return PatternResult(symbol=bar.symbol, pattern="marubozu", bullish=is_bullish_candle)

    return PatternResult(symbol=bar.symbol, pattern=None, bullish=None)


@dataclass
class CandlePatternTracker:
    _results: dict[str, PatternResult] = field(default_factory=dict)

    def record(self, bar: OHLCVBar) -> PatternResult:
        result = detect_pattern(bar)
        self._results[bar.symbol.upper()] = result
        return result

    def get(self, symbol: str) -> Optional[PatternResult]:
        return self._results.get(symbol.upper())

    def all_results(self) -> list[PatternResult]:
        return list(self._results.values())
