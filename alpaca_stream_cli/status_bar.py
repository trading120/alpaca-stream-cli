"""Status bar rendering for connection state, latency, and session info."""

from datetime import datetime, timezone
from typing import Optional

from rich.text import Text
from rich.table import Table
from rich.console import Console

from alpaca_stream_cli.connection_monitor import ConnectionMonitor, ConnectionStatus
from alpaca_stream_cli.latency_tracker import LatencyTracker


def _status_color(status: ConnectionStatus) -> str:
    return {
        ConnectionStatus.CONNECTED: "green",
        ConnectionStatus.DISCONNECTED: "red",
        ConnectionStatus.RECONNECTING: "yellow",
    }.get(status, "white")


def _fmt_uptime(seconds: Optional[float]) -> str:
    if seconds is None:
        return "--"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_latency(tracker: LatencyTracker, symbol: Optional[str] = None) -> str:
    if symbol:
        avg = tracker.average_ms(symbol)
        return f"{avg:.1f}ms" if avg is not None else "--"
    # global average across all tracked symbols
    samples = [
        tracker.average_ms(s)
        for s in tracker.symbols()
        if tracker.average_ms(s) is not None
    ]
    if not samples:
        return "--"
    return f"{sum(samples) / len(samples):.1f}ms"


def build_status_bar(
    monitor: ConnectionMonitor,
    tracker: LatencyTracker,
    symbol_count: int = 0,
    alert_count: int = 0,
) -> Table:
    """Build a single-row status bar table."""
    status = monitor.status
    color = _status_color(status)
    uptime = _fmt_uptime(monitor.uptime_seconds)
    reconnects = monitor.reconnect_count
    latency = _fmt_latency(tracker)
    now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

    table = Table.grid(padding=(0, 2))
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_column()
    table.add_column()

    table.add_row(
        Text(f"● {status.value.upper()}", style=f"bold {color}"),
        Text(f"Uptime: {uptime}", style="dim"),
        Text(f"Reconnects: {reconnects}", style="dim"),
        Text(f"Latency: {latency}", style="cyan"),
        Text(f"Symbols: {symbol_count}", style="dim"),
        Text(f"Alerts: {alert_count}  {now}", style="dim"),
    )
    return table
