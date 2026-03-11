from __future__ import annotations
from typing import Dict, Any, List
from integrations.longbridge_adapter import submit_order


def submit_orders(orders: List[Dict[str, Any]], mode: str = "SIMULATE") -> Dict[str, Any]:
    results = []
    for order in orders:
        if mode != "LIVE":
            results.append({
                "symbol": order.get("symbol", ""),
                "action": order.get("action", "HOLD"),
                "shares": order.get("shares", 0),
                "price": order.get("price"),
                "status": "simulated",
                "mode": mode,
            })
        else:
            res = submit_order(order.get("symbol", ""), int(order.get("shares", 0)), side=order.get("action", "BUY"), submitted_price=order.get("price"))
            results.append({
                "symbol": order.get("symbol", ""),
                "action": order.get("action", "BUY"),
                "shares": order.get("shares", 0),
                "price": order.get("price"),
                "status": res.get("status", "submitted"),
                "order_id": res.get("order_id", ""),
                "mode": mode,
            })
    return {"results": results}
