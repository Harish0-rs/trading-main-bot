from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def _validate_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not cleaned.isalnum():
        raise ValueError(f"Symbol '{symbol}' must contain only alphanumeric characters.")
    return cleaned


def _validate_side(side: str) -> str:
    upper = side.strip().upper()
    if upper not in VALID_SIDES:
        raise ValueError(f"Side '{side}' is invalid. Must be one of: {', '.join(sorted(VALID_SIDES))}.")
    return upper


def _validate_order_type(order_type: str) -> str:
    upper = order_type.strip().upper()
    if upper not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Order type '{order_type}' is invalid. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return upper


def _validate_quantity(quantity: float) -> float:
    if quantity <= 0:
        raise ValueError(f"Quantity must be greater than zero, got {quantity}.")
    return quantity


def _validate_price(price: float | None, field_name: str = "Price") -> float | None:
    if price is None:
        return None
    if price <= 0:
        raise ValueError(f"{field_name} must be greater than zero, got {price}.")
    return price


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> dict:
    validated_type = _validate_order_type(order_type)

    if validated_type == "LIMIT" and price is None:
        raise ValueError("LIMIT orders require --price to be specified.")
    if validated_type == "STOP_MARKET" and stop_price is None:
        raise ValueError("STOP_MARKET orders require --stop-price to be specified.")

    return {
        "symbol": _validate_symbol(symbol),
        "side": _validate_side(side),
        "order_type": validated_type,
        "quantity": _validate_quantity(quantity),
        "price": _validate_price(price, "Price"),
        "stop_price": _validate_price(stop_price, "Stop price"),
    }
