from __future__ import annotations
from collections import defaultdict
from typing import Dict, Any, List
from utils.math_utils import safe_float
from integrations.longbridge_adapter import longport_available, fetch_account_balance, fetch_stock_positions

DEFAULT_POSITIONS = [
    {"symbol": "NVDA", "shares": 136, "cost": 179.800},
    {"symbol": "SOXX", "shares": 77, "cost": 311.200},
    {"symbol": "AVGO", "shares": 25, "cost": 339.083},
    {"symbol": "MSFT", "shares": 11, "cost": 410.000},
    {"symbol": "META", "shares": 9, "cost": 654.444},
    {"symbol": "GOOGL", "shares": 10, "cost": 298.000},
    {"symbol": "ANET", "shares": 5, "cost": 138.570},
    {"symbol": "TSLA", "shares": 21, "cost": 319.911},
    {"symbol": "IVV", "shares": 10, "cost": 659.522},
    {"symbol": "SCHD", "shares": 73, "cost": 26.780},
    {"symbol": "JNJ", "shares": 45, "cost": 185.009},
    {"symbol": "MUFG", "shares": 80, "cost": 19.250},
]
DEFAULT_CASH = 12486.58


def _build_default_positions() -> List[Dict[str, Any]]:
    return [dict(x) for x in DEFAULT_POSITIONS]


def calculate_portfolio_weights(positions: List[Dict[str, Any]], total_equity: float | None = None) -> Dict[str, float]:
    total_value = total_equity if total_equity is not None else sum(float(p.get("value", 0.0)) for p in positions)
    if total_value <= 0:
        return {}
    return {p["symbol"]: round(float(p.get("value", 0.0)) / total_value, 4) for p in positions if p.get("symbol")}


def _aggregate_longbridge_positions(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    bucket = defaultdict(lambda: {"shares": 0, "cost_value": 0.0, "available_quantity": 0, "currency": "USD", "symbol_name": ""})
    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        shares = int(row.get("shares", 0) or 0)
        cost = safe_float(row.get("cost", 0.0), 0.0)
        if not symbol or shares <= 0:
            continue
        item = bucket[symbol]
        item["shares"] += shares
        item["cost_value"] += shares * cost
        item["available_quantity"] += int(row.get("available_quantity", 0) or 0)
        item["currency"] = row.get("currency", item["currency"]) or item["currency"]
        item["symbol_name"] = row.get("symbol_name", item["symbol_name"]) or item["symbol_name"]
    out = []
    for symbol, item in bucket.items():
        shares = item["shares"]
        avg_cost = item["cost_value"] / shares if shares > 0 else 0.0
        out.append({
            "symbol": symbol,
            "shares": shares,
            "cost": round(avg_cost, 4),
            "available_quantity": item["available_quantity"],
            "currency": item["currency"],
            "symbol_name": item["symbol_name"],
        })
    return sorted(out, key=lambda x: x["symbol"])


def _pick_cash_and_equity(balance_rows: List[Dict[str, Any]], fallback_cash: float):
    cash = fallback_cash
    total_equity = 0.0
    if balance_rows:
        target = next((x for x in balance_rows if str(x.get("currency", "")).upper() == "USD"), balance_rows[0])
        total_equity = safe_float(target.get("net_assets", 0.0), 0.0)
        cash_infos = target.get("cash_infos", []) or []
        if cash_infos:
            ci = next((x for x in cash_infos if str(x.get("currency", "")).upper() == "USD"), cash_infos[0])
            cash = safe_float(ci.get("available_cash", fallback_cash), fallback_cash)
        else:
            cash = safe_float(target.get("total_cash", fallback_cash), fallback_cash)
    return round(cash, 2), round(total_equity, 2)


def sync_portfolio(event: Dict[str, Any] | None = None) -> Dict[str, Any]:
    event = event or {}
    quote_map = event.get("quote_map", {})
    use_longbridge = bool(event.get("use_longbridge", True))
    cash = safe_float(event.get("cash", DEFAULT_CASH), DEFAULT_CASH)
    source = "STATIC_BASELINE"
    longbridge_error = ""
    broker_balances: List[Dict[str, Any]] = []
    longbridge_positions: List[Dict[str, Any]] = []
    if use_longbridge and longport_available():
        try:
            broker_balances = fetch_account_balance("USD")
            longbridge_positions = fetch_stock_positions()
            source = "LONGBRIDGE_LIVE"
        except Exception as exc:
            longbridge_error = str(exc)
            source = "STATIC_BASELINE"
    basis_positions = _aggregate_longbridge_positions(longbridge_positions) if longbridge_positions else _build_default_positions()
    if broker_balances:
        cash, broker_equity = _pick_cash_and_equity(broker_balances, cash)
    else:
        broker_equity = 0.0
    positions = []
    invested_value = 0.0
    for item in basis_positions:
        symbol = item["symbol"]
        shares = int(item.get("shares", 0))
        cost = safe_float(item.get("cost", 0.0), 0.0)
        price = safe_float(quote_map.get(symbol, {}).get("price", cost), cost)
        value = round(price * shares, 2)
        invested_value += value
        positions.append({
            "symbol": symbol,
            "shares": shares,
            "cost": round(cost, 4),
            "price": round(price, 2),
            "value": value,
            "cost_value": round(cost * shares, 2),
            "pnl": round(value - cost * shares, 2),
            "available_quantity": int(item.get("available_quantity", shares)),
            "currency": item.get("currency", "USD"),
            "symbol_name": item.get("symbol_name", ""),
        })
    portfolio_value = round(invested_value + cash, 2)
    if broker_equity > 0:
        portfolio_value = round(max(portfolio_value, broker_equity), 2)
    weights = calculate_portfolio_weights(positions, portfolio_value)
    for p in positions:
        p["weight"] = weights.get(p["symbol"], 0.0)
    return {
        "positions": positions,
        "cash": round(cash, 2),
        "portfolio_value": portfolio_value,
        "weights": weights,
        "source": source,
        "longbridge_error": longbridge_error,
        "broker_balances": broker_balances,
    }
