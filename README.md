# alpaca-stream-cli

A terminal-based real-time market data viewer for Alpaca's streaming API with configurable watchlists and alerts.

---

## Installation

```bash
pip install alpaca-stream-cli
```

Or install from source:

```bash
git clone https://github.com/youruser/alpaca-stream-cli.git
cd alpaca-stream-cli
pip install -e .
```

---

## Configuration

Set your Alpaca API credentials as environment variables:

```bash
export ALPACA_API_KEY=your_api_key
export ALPACA_SECRET_KEY=your_secret_key
```

---

## Usage

Start streaming quotes for a watchlist:

```bash
alpaca-stream --symbols AAPL TSLA NVDA
```

Load a saved watchlist and set a price alert:

```bash
alpaca-stream --watchlist tech.json --alert AAPL above 190.00
```

Run in paper trading mode:

```bash
alpaca-stream --symbols MSFT AMZN --paper
```

**Keyboard shortcuts while running:**

| Key | Action |
|-----|--------|
| `q` | Quit |
| `a` | Add symbol |
| `r` | Remove symbol |
| `s` | Save current watchlist |

---

## Requirements

- Python 3.8+
- Alpaca brokerage account ([sign up here](https://alpaca.markets))

---

## License

MIT © 2024 — see [LICENSE](LICENSE) for details.