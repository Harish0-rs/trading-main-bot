"""
main.py — Entry point for the Binance USDT-M Futures Testnet CLI Trading Bot.

Usage:
    python main.py --help
    python main.py menu          # interactive mode
    python main.py price BTCUSDT
    python main.py balance
    python main.py positions
    python main.py open-orders
    python main.py order --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
    python main.py cancel --symbol BTCUSDT --order-id 123456
    python main.py history --symbol BTCUSDT --limit 20
"""

from bot.cli import app

if __name__ == "__main__":
    app()
