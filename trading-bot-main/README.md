# ⚡ Binance USDT-M Futures Testnet CLI Trading Bot

A production-quality, CLI-based trading bot for the **Binance USDT-M Futures Testnet**, built with Python 3.10+, Typer, Rich, and requests.

---

## Features

| Feature | Detail |
|---|---|
| **HMAC-SHA256 signing** | All authenticated endpoints signed per Binance specification |
| **Rich terminal output** | Colour-coded tables, panels, and status messages |
| **Interactive menu** | Full-featured terminal UI via `menu` command |
| **7 sub-commands** | `price`, `balance`, `positions`, `open-orders`, `order`, `cancel`, `history` |
| **Confirmation prompts** | Prevents accidental order placement |
| **Rotating log files** | Debug-level logs written to `logs/trading_bot.log` |
| **Input validation** | Symbol, side, type, quantity, and price validated before any API call |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── cli.py            # Typer commands + interactive menu
│   ├── client.py         # HMAC-signed Binance REST client
│   ├── display.py        # Rich terminal output helpers
│   ├── logging_config.py # Rotating file + console logging
│   ├── orders.py         # Business logic / order manager
│   └── validators.py     # Input validation
├── logs/                 # Auto-created at runtime
├── main.py               # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # macOS / Linux
```

Edit `.env` with your **Binance Futures Testnet** API key and secret.  
Get them at: <https://testnet.binancefuture.com>

```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

---

## Usage

### Interactive menu (recommended for beginners)

```bash
python main.py menu
```

### CLI sub-commands

```bash
# Show help
python main.py --help

# Live price
python main.py price BTCUSDT

# Account balance
python main.py balance

# Open positions
python main.py positions

# Open orders (all, or filter by symbol)
python main.py open-orders
python main.py open-orders --symbol BTCUSDT

# Place an order
python main.py order --symbol BTCUSDT --side BUY  --type MARKET --qty 0.001
python main.py order --symbol BTCUSDT --side SELL --type LIMIT  --qty 0.001 --price 80000
python main.py order --symbol BTCUSDT --side SELL --type STOP_MARKET --qty 0.001 --stop-price 75000

# Cancel an order
python main.py cancel --symbol BTCUSDT --order-id 123456789

# Order history
python main.py history --symbol BTCUSDT --limit 20
```

### Skip confirmation prompt

```bash
python main.py order --symbol BTCUSDT --side BUY --type MARKET --qty 0.001 --no-confirm
```

---

## Logging

All debug-level API calls and responses are written to `logs/trading_bot.log` (rotated at 5 MB, 3 backups).  
Only `WARNING` and above appear in the terminal.

---

## Disclaimer

This bot targets the **Binance Futures Testnet** only. Use on mainnet at your own risk. This is not financial advice.
