from __future__ import annotations
from datetime import datetime, timezone
from config.version_loader import load_version_info
from utils.idempotency import build_order_key, check_order_exists, save_order_key
from utils.math_utils import safe_float

def check_duplicate_order(order):
    version = load_version_info().get("version", "unknown")
    today = datetime.now(timezone.utc).date().isoformat()
    payload = dict(order)
    payload["trade_date"] = today
    key = build_order_key(payload, version)
    if check_order_exists(key):
        return {"passed": False, "reason": f"duplicate order blocked: {key}"}
    save_order_key(key, payload)
    return {"passed": True, "reason": "duplicate check passed"}

def check_cash_sufficiency(order, portfolio, params):
    cash = safe_float(portfolio.get("cash", 0.0), 0.0)
    budget = safe_float(order.get("budget", 0.0), 0.0)
    if budget > cash:
        return {"passed": False, "reason": "insufficient cash"}
    return {"passed": True, "reason": "cash sufficient"}

def check_order_limits(order, params):
    max_order_value = safe_float(params["position"]["max_order_value"], 5000.0)
    budget = safe_float(order.get("budget", 0.0), 0.0)
    shares = int(order.get("shares", 0))
    if shares <= 0:
        return {"passed": False, "reason": "shares must be positive"}
    if budget > max_order_value:
        return {"passed": False, "reason": "budget exceeds max order value"}
    return {"passed": True, "reason": "order within limits"}

def guard_orders(position_plan, portfolio, risk, params=None):
    params = params or {}
    orders = position_plan.get("orders", [])
    if risk.get("status") in ("ALERT","RISK_STOP"):
        return {"approved_orders": [], "blocked_orders": [{"order": o, "reason": f'{risk.get("status")} blocks all new orders'} for o in orders]}
    approved, blocked = [], []
    for order in orders:
        checks = [check_duplicate_order(order), check_cash_sufficiency(order, portfolio, params), check_order_limits(order, params)]
        failed = next((c for c in checks if not c["passed"]), None)
        if failed:
            blocked.append({"order": order, "reason": failed["reason"]})
        else:
            approved.append(order)
    return {"approved_orders": approved, "blocked_orders": blocked}
