from __future__ import annotations
from typing import Dict, Any, List


def apply_slippage(price: float, params: Dict[str, Any]) -> float:
    return price * (1 + float(params["backtest"]["slippage_bps"]) / 10000.0)


def apply_fees(order_value: float, params: Dict[str, Any]) -> float:
    return order_value * float(params["backtest"]["fee_rate"])


def _mark_to_market(positions: List[Dict[str, Any]], next_open_prices: Dict[str, Any], cash: float) -> float:
    total = cash
    for pos in positions:
        symbol = pos["symbol"]
        mark_price = float(next_open_prices.get(symbol, {}).get("price", pos.get("price", 0.0)))
        pos["price"] = round(mark_price, 2)
        pos["value"] = round(mark_price * pos["shares"], 2)
        total += pos["value"]
    return round(total, 2)


def simulate_execution(order_plan: Dict[str, Any], next_open_prices: Dict[str, Any], portfolio: Dict[str, Any], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    params = params or {}
    trades: List[Dict[str, Any]] = []
    cash = float(portfolio.get("cash", 0.0))
    positions = [dict(p) for p in portfolio.get("positions", [])]
    for order in order_plan.get("orders", []):
        if str(order.get("action", "BUY")).upper() != "BUY":
            continue
        symbol = order["symbol"]
        shares = int(order.get("shares", 0))
        open_price = float(next_open_prices.get(symbol, {}).get("price", order.get("price", 0.0)))
        exec_price = apply_slippage(open_price, params)
        order_value = exec_price * shares
        fees = apply_fees(order_value, params)
        total_cost = order_value + fees
        if shares <= 0 or total_cost > cash:
            continue
        cash -= total_cost
        positions.append({
            "symbol": symbol,
            "shares": shares,
            "cost": round(exec_price, 4),
            "price": round(exec_price, 2),
            "value": round(order_value, 2),
            "cost_value": round(order_value, 2),
            "pnl": 0.0,
        })
        trades.append({
            "symbol": symbol,
            "action": "BUY",
            "shares": shares,
            "exec_price": round(exec_price, 4),
            "fees": round(fees, 4),
            "order_value": round(order_value, 2),
        })
    portfolio_value = _mark_to_market(positions, next_open_prices, cash)
    return {"trades": trades, "portfolio": {"cash": round(cash, 2), "positions": positions, "portfolio_value": portfolio_value}}
