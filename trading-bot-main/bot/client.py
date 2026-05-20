from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"
REQUEST_TIMEOUT = 10


class BinanceClient:
    def __init__(self) -> None:
        self._api_key = os.environ.get("BINANCE_API_KEY", "")
        self._api_secret = os.environ.get("BINANCE_API_SECRET", "")
        if not self._api_key or not self._api_secret:
            raise RuntimeError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file."
            )
        self._session = requests.Session()
        self._session.headers.update({"X-MBX-APIKEY": self._api_key})

    def _sign(self, params: dict) -> dict:
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return {**params, "signature": signature}

    def _signed_params(self, params: dict | None) -> dict:
        """Return a fresh copy of params with timestamp + signature added."""
        p = dict(params or {})
        p["timestamp"] = int(time.time() * 1000)
        return self._sign(p)

    def _get(self, path: str, params: dict | None = None, signed: bool = False) -> dict | list:
        url = f"{BASE_URL}{path}"
        query_params = self._signed_params(params) if signed else dict(params or {})
        logger.debug("GET %s params=%s", url, {k: v for k, v in query_params.items() if k != "signature"})
        return self._execute(self._session.get, url, params=query_params)

    def _post(self, path: str, params: dict) -> dict:
        url = f"{BASE_URL}{path}"
        signed_params = self._signed_params(params)
        logger.debug("POST %s params=%s", url, {k: v for k, v in signed_params.items() if k != "signature"})
        return self._execute(self._session.post, url, params=signed_params)

    def _delete(self, path: str, params: dict) -> dict:
        url = f"{BASE_URL}{path}"
        signed_params = self._signed_params(params)
        logger.debug("DELETE %s params=%s", url, {k: v for k, v in signed_params.items() if k != "signature"})
        return self._execute(self._session.delete, url, params=signed_params)

    def _execute(self, method, url: str, **kwargs) -> dict | list:
        try:
            response = method(url, timeout=REQUEST_TIMEOUT, **kwargs)
            logger.debug("Response %s: %s", response.status_code, response.text[:500])
            if not response.ok:
                try:
                    error_body = response.json()
                    code = error_body.get("code", response.status_code)
                    msg = error_body.get("msg", response.text)
                except Exception:
                    code = response.status_code
                    msg = response.text
                if code == -2015:
                    raise RuntimeError(
                        "Binance API error -2015: Invalid API key.\n"
                        "  → Your .env file still has placeholder keys.\n"
                        "  → Go to https://testnet.binancefuture.com → log in → generate API keys\n"
                        "  → Paste them into your .env file and restart the bot."
                    )
                raise RuntimeError(f"Binance API error {code}: {msg}")
            return response.json()
        except requests.ConnectionError as exc:
            raise RuntimeError(f"Connection failed — check your network: {exc}") from exc
        except requests.Timeout:
            raise RuntimeError(f"Request timed out after {REQUEST_TIMEOUT}s.")
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Unexpected HTTP error: {exc}") from exc

    def get_symbols(self) -> list[str]:
        """Return all TRADING status perpetual USDT symbols (public endpoint — no auth needed)."""
        url = f"{BASE_URL}/fapi/v1/exchangeInfo"
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            raise RuntimeError(f"Could not fetch exchange info: {exc}") from exc
        return sorted(
            s["symbol"]
            for s in data.get("symbols", [])
            if s.get("status") == "TRADING" and s.get("symbol", "").endswith("USDT")
        )

    def get_price(self, symbol: str) -> dict:
        return self._get("/fapi/v1/ticker/price", params={"symbol": symbol})

    def get_balance(self) -> list:
        return self._get("/fapi/v2/balance", signed=True)

    def get_positions(self) -> list:
        return self._get("/fapi/v2/positionRisk", signed=True)

    def get_open_orders(self, symbol: str | None = None) -> list:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._get("/fapi/v1/openOrders", params=params, signed=True)

    def place_order(self, payload: dict) -> dict:
        return self._post("/fapi/v1/order", payload)

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        return self._delete("/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})

    def get_order_history(self, symbol: str, limit: int) -> list:
        return self._get("/fapi/v1/allOrders", params={"symbol": symbol, "limit": limit}, signed=True)
