"""Formatting utilities for price, volume, and percentage display."""

from typing import Optional


PRICE_PRECISION = 2
VOLUME_ABBREV_THRESHOLD = 1_000


def format_price(price: Optional[float], currency: str = "$") -> str:
    """Format a price value with currency symbol."""
    if price is None:
        return "--"
    return f"{currency}{price:,.{PRICE_PRECISION}f}"


def format_volume(volume: Optional[int]) -> str:
    """Format a volume value with K/M/B abbreviations."""
    if volume is None:
        return "--"
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    if volume >= VOLUME_ABBREV_THRESHOLD:
        return f"{volume / 1_000:.1f}K"
    return str(volume)


def format_percent(value: Optional[float], include_sign: bool = True) -> str:
    """Format a percentage value with optional +/- sign."""
    if value is None:
        return "--"
    sign = "+" if include_sign and value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_spread(bid: Optional[float], ask: Optional[float]) -> str:
    """Format bid/ask spread as a string."""
    if bid is None or ask is None:
        return "--"
    spread = ask - bid
    return f"{format_price(spread)} ({format_percent(spread / bid * 100 if bid else None)})"


def color_for_change(change: Optional[float]) -> str:
    """Return a Rich color string based on the sign of a change value."""
    if change is None:
        return "white"
    if change > 0:
        return "green"
    if change < 0:
        return "red"
    return "white"


def format_price_change(current: Optional[float], previous: Optional[float]) -> str:
    """Format the absolute and percentage change between two prices."""
    if current is None or previous is None or previous == 0:
        return "--"
    change = current - previous
    pct = (change / previous) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.2f} ({sign}{pct:.2f}%)"
