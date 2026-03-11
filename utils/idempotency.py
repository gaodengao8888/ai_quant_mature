from __future__ import annotations
_ORDER_STORE = {}

def build_order_key(order: dict, version: str) -> str:
    trade_date = str(order.get("trade_date", "UNKNOWN_DATE"))
    symbol = str(order.get("symbol", "UNKNOWN"))
    action = str(order.get("action", "HOLD")).upper()
    shares = int(order.get("shares", 0))
    return f"{trade_date}|{symbol}|{action}|{shares}|{version}"

def check_order_exists(order_key: str) -> bool:
    return order_key in _ORDER_STORE

def save_order_key(order_key: str, payload: dict) -> None:
    _ORDER_STORE[order_key] = payload
