"""Sparkline renderer for in-terminal price history visualization."""
from typing import Optional
from alpaca_stream_cli.history import PriceHistory

# Unicode block characters ordered from low to high
_BLOCKS = " ▁▂▃▄▅▆▇█"
_NUM_BLOCKS = len(_BLOCKS) - 1  # exclude space as a level


def _normalize(values: list[float]) -> list[float]:
    """Normalize a list of floats to the range [0, 1]."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def sparkline(values: list[float], width: int = 20) -> str:
    """Render a sparkline string from a list of price values.

    Args:
        values: Ordered list of price floats (oldest first).
        width:  Number of characters in the output sparkline.

    Returns:
        A unicode sparkline string, or an empty string if insufficient data.
    """
    if len(values) < 2:
        return ""

    # Sample or use the tail of values to fit the requested width
    if len(values) > width:
        step = len(values) / width
        values = [values[int(i * step)] for i in range(width)]
    else:
        width = len(values)

    normalized = _normalize(values)
    return "".join(_BLOCKS[round(n * _NUM_BLOCKS)] for n in normalized)


def sparkline_for_symbol(
    symbol: str,
    history: PriceHistory,
    width: int = 20,
) -> Optional[str]:
    """Build a sparkline for a symbol using its recorded price history.

    Args:
        symbol:  Ticker symbol (case-insensitive).
        history: PriceHistory instance containing recorded points.
        width:   Desired character width of the sparkline.

    Returns:
        A sparkline string, or None if there is insufficient history.
    """
    points = history.get(symbol)
    if len(points) < 2:
        return None
    prices = [p.price for p in points]
    return sparkline(prices, width=width)
