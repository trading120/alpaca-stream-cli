"""Rich display helpers for volume spike data."""
from __future__ import annotations

from typing import Dict

from rich.table import Table
from rich import box

from alpaca_stream_cli.volume_spike import VolumeSpikeResult


def _spike_color(ratio: float) -> str:
    if ratio >= 4.0:
        return "bold red"
    if ratio >= 2.0:
        return "yellow"
    if ratio >= 1.0:
        return "green"
    return "dim"


def _fmt_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "--"
    return f"{ratio:.2f}x"


def _fmt_volume(volume: float | None) -> str:
    if volume is None:
        return "--"
    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    if volume >= 1_000:
        return f"{volume / 1_000:.1f}K"
    return f"{volume:.0f}"


def build_volume_spike_table(
    results: Dict[str, VolumeSpikeResult],
    max_rows: int = 20,
) -> Table:
    """Build a Rich Table showing volume spike data per symbol."""
    table = Table(
        title="Volume Spikes",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=6)
    table.add_column("Volume", justify="right", min_width=8)
    table.add_column("Baseline", justify="right", min_width=8)
    table.add_column("Ratio", justify="right", min_width=7)
    table.add_column("Spike", justify="center", min_width=5)

    sorted_results = sorted(
        results.values(),
        key=lambda r: r.ratio,
        reverse=True,
    )[:max_rows]

    for r in sorted_results:
        color = _spike_color(r.ratio)
        spike_indicator = "[bold red]YES[/]" if r.is_spike else "[dim]no[/]"
        table.add_row(
            f"[{color}]{r.symbol}[/]",
            f"[{color}]{_fmt_volume(r.current_volume)}[/]",
            _fmt_volume(r.baseline_volume),
            f"[{color}]{_fmt_ratio(r.ratio)}[/]",
            spike_indicator,
        )

    return table
