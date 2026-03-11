from __future__ import annotations
from execution.order_executor_longbridge import submit_orders


def normalize_trade_action(order):
    out = dict(order)
    out["action"] = str(order.get("action", "HOLD")).upper()
    return out


def execute_trades(order_plan, mode="SIMULATE"):
    approved = [normalize_trade_action(o) for o in order_plan.get("approved_orders", [])]
    execution = submit_orders(approved, mode=mode) if approved else {"results": []}
    return {"mode": mode, "results": execution.get("results", []), "blocked_orders": order_plan.get("blocked_orders", [])}
