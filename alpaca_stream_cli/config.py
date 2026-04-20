"""Configuration management for alpaca-stream-cli."""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional

DEFAULT_CONFIG_PATH = os.path.expanduser("~/.alpaca_stream_cli/config.json")


@dataclass
class AlertConfig:
    symbol: str
    price_above: Optional[float] = None
    price_below: Optional[float] = None
    volume_above: Optional[int] = None


@dataclass
class AppConfig:
    api_key: str = ""
    api_secret: str = ""
    base_url: str = "https://paper-api.alpaca.markets"
    data_stream_url: str = "wss://stream.data.alpaca.markets/v2/iex"
    watchlist: List[str] = field(default_factory=lambda: ["AAPL", "MSFT", "TSLA"])
    alerts: List[AlertConfig] = field(default_factory=list)
    refresh_interval_ms: int = 500
    max_rows: int = 20


def load_config(path: str = DEFAULT_CONFIG_PATH) -> AppConfig:
    """Load configuration from a JSON file, falling back to env vars."""
    config = AppConfig()

    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        alerts_raw = data.pop("alerts", [])
        config = AppConfig(**{k: v for k, v in data.items() if hasattr(AppConfig, k)})
        config.alerts = [AlertConfig(**a) for a in alerts_raw]

    config.api_key = os.environ.get("ALPACA_API_KEY", config.api_key)
    config.api_secret = os.environ.get("ALPACA_API_SECRET", config.api_secret)

    return config


def save_config(config: AppConfig, path: str = DEFAULT_CONFIG_PATH) -> None:
    """Persist configuration to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = asdict(config)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
