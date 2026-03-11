from __future__ import annotations
from typing import Dict, Any
from config.strategy_params import STRATEGY_PARAMS
from utils.math_utils import safe_float, safe_int


def _rank_signal(signal: Dict[str, Any]) -> int:
    sig = signal.get("signal", "")
    return 2 if sig == "BREAKOUT_BUY" else 1 if sig == "PULLBACK_BUY" else 0


def get_ai_cycle_multiplier(ai_cycle, params):
    return safe_float(params["ai_cycle"]["cycle_state_multipliers"].get(ai_cycle.get("ai_cycle", "AI_CONSOLIDATION"), 1.0), 1.0)


def get_market_regime_multiplier(market_regime, params):
    return safe_float(params["market_regime"]["regime_multipliers"].get(market_regime.get("market_regime", "SIDEWAYS"), 1.0), 1.0)


def get_risk_multiplier(risk, params):
    return safe_float(params["risk"]["risk_multipliers"].get(risk.get("status", "SAFE"), 1.0), 1.0)


def get_crowding_multiplier(risk, params):
    crowding = risk.get("crowding", "LOW")
    return safe_float(params["risk"]["crowding_multipliers"].get(crowding, 1.0), 1.0)


def _cash_multiplier(cash: float, portfolio_value: float, params: Dict[str, Any]) -> float:
    base = float(params["position"]["base_order_budget"])
    min_cash_buffer_ratio = float(params["position"]["min_cash_buffer_ratio"])
    available_cash = max(0.0, cash - portfolio_value * min_cash_buffer_ratio)
    if available_cash >= base:
        return float(params["position"]["cash_multiplier_bands"]["ample"])
    if available_cash >= base * 0.7:
        return float(params["position"]["cash_multiplier_bands"]["tight"])
    if available_cash >= base * 0.3:
        return float(params["position"]["cash_multiplier_bands"]["very_tight"])
    return float(params["position"]["cash_multiplier_bands"]["none"])


def calculate_shares(order_budget, price):
    if price <= 0:
        return 0
    return safe_int(order_budget / price, 0)


def calculate_positions(filtered_signals, portfolio, risk, ai_cycle, market_regime, params=None):
    params = params or STRATEGY_PARAMS
    passed = filtered_signals.get("passed", [])
    if not passed:
        return {"orders": [], "blocked_reason": "no passed signals"}
    if risk.get("status") in ("ALERT", "RISK_STOP"):
        return {"orders": [], "blocked_reason": f"risk status {risk.get('status')} blocks buy"}
    selected = sorted(passed, key=lambda x: (_rank_signal(x), safe_float(x.get("confidence", 0.0), 0.0), safe_float(x.get("price", 0.0), 0.0)), reverse=True)[0]
    price = safe_float(selected.get("price", 0.0), 0.0)
    cash = safe_float(portfolio.get("cash", 0.0), 0.0)
    portfolio_value = safe_float(portfolio.get("portfolio_value", 0.0), 0.0)
    base_order_budget = float(params["position"]["base_order_budget"])
    max_order_value = float(params["position"]["max_order_value"])
    budget = base_order_budget * get_ai_cycle_multiplier(ai_cycle, params) * get_market_regime_multiplier(market_regime, params) * get_risk_multiplier(risk, params) * get_crowding_multiplier(risk, params) * _cash_multiplier(cash, portfolio_value, params)
    budget = min(budget, max_order_value, cash)
    shares = calculate_shares(budget, price)
    if shares < int(params["position"]["min_shares_required"]):
        return {"orders": [], "blocked_reason": "budget insufficient for minimum shares"}
    return {
        "orders": [{
            "symbol": selected.get("symbol", ""),
            "action": "BUY",
            "signal": selected.get("signal", ""),
            "shares": shares,
            "budget": round(budget, 2),
            "price": round(price, 2),
            "estimated_value": round(shares * price, 2),
            "reason": selected.get("reason", selected.get("signal", "")),
        }]
    }
