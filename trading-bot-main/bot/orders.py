from __future__ import annotations

import logging

from bot.client import BinanceClient
from bot.validators import validate_order_params

logger = logging.getLogger(__name__)


class OrderManager:
    def __init__(self) -> None:
        self._client = BinanceClient()

    def get_symbols(self) -> list[str]:
        """Fetch all tradeable USDT perpetual symbols from testnet."""
        return self._client.get_symbols()

    def get_price(self, symbol: str) -> dict:
        logger.info("Fetching price for %s", symbol)
        return self._client.get_price(symbol.upper())

    def get_balance(self) -> list[dict]:
        logger.info("Fetching account balance")
        raw = self._client.get_balance()
        return [item for item in raw if float(item.get("balance", 0)) != 0]

    def get_positions(self) -> list[dict]:
        logger.info("Fetching open positions")
        raw = self._client.get_positions()
        return [pos for pos in raw if float(pos.get("positionAmt", 0)) != 0]

    def get_open_orders(self, symbol: str | None = None) -> list[dict]:
        logger.info("Fetching open orders, symbol=%s", symbol)
        return self._client.get_open_orders(symbol=symbol.upper() if symbol else None)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
    ) -> tuple[dict, dict]:
        params = validate_order_params(symbol, side, order_type, quantity, price, stop_price)
        logger.info(
            "Placing order: symbol=%s side=%s type=%s qty=%s",
            params["symbol"],
            params["side"],
            params["order_type"],
            params["quantity"],
        )

        payload: dict = {
            "symbol": params["symbol"],
            "side": params["side"],
            "type": params["order_type"],
            "quantity": params["quantity"],
        }

        if params["order_type"] == "LIMIT":
            payload["price"] = params["price"]
            payload["timeInForce"] = "GTC"

        if params["order_type"] == "STOP_MARKET":
            payload["stopPrice"] = params["stop_price"]

        response = self._client.place_order(payload)
        logger.info("Order placed successfully: orderId=%s", response.get("orderId"))
        return params, response

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        logger.info("Cancelling order: symbol=%s orderId=%s", symbol, order_id)
        return self._client.cancel_order(symbol.upper(), order_id)

    def get_order_history(self, symbol: str, limit: int) -> list[dict]:
        logger.info("Fetching order history: symbol=%s limit=%s", symbol, limit)
        return self._client.get_order_history(symbol.upper(), limit)
