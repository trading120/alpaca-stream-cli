"""Rich display for tick aggregator bucket data."""
from __future__ import annotations

from typing import List

from rich.table import Table
from rich import box

from alpaca_stream_cli.tick_aggregator import TickBucket


def _change_color(change: float) -> str:
    if change > 0:
        return "bold green"
    if change < 0:
        return "bold red"
    return "white"


def _fmt_price(v: float) -> str:
    return f"${v:,.4f}"


def _fmt_volume(v: float) -> str:
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"{v / 1_000:.1f}K"
    return f"{v:.0f}"


def _fmt_change(bucket: TickBucket) -> str:
    pct = bucket.change_pct
    sign = "+" if bucket.change >= 0 else ""
    if pct is None:
        return f"{sign}{bucket.change:.4f}"
    return f"{sign}{bucket.change:.4f} ({sign}{pct:.2f}%)"


def build_tick_bucket_table(
    buckets: List[TickBucket],
    *,
    title: str = "Tick Buckets",
    max_rows: int = 50,
) -> Table:
    """Build a Rich table from a list of TickBucket records."""
    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", no_wrap=True)
    table.add_column("Time", style="dim")
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right", style="green")
    table.add_column("Low", justify="right", style="red")
    table.add_column("Close", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Trades", justify="right")

    for bucket in buckets[:max_rows]:
        color = _change_color(bucket.change)
        table.add_row(
            bucket.symbol,
            bucket.bucket_ts.strftime("%H:%M:%S"),
            _fmt_price(bucket.open),
            _fmt_price(bucket.high),
            _fmt_price(bucket.low),
            f"[{color}]{_fmt_price(bucket.close)}[/{color}]",
            f"[{color}]{_fmt_change(bucket)}[/{color}]",
            _fmt_volume(bucket.volume),
            str(bucket.trade_count),
        )

    return table
