from __future__ import annotations
from typing import Dict, Any, List
from config.strategy_params import STRATEGY_PARAMS
from utils.math_utils import safe_float

AI_CLUSTER = {"NVDA", "SOXX", "AVGO", "MSFT", "META", "GOOGL", "ANET", "TSLA", "AMD", "TSM"}


def detect_overweight_positions(portfolio: Dict[str, Any], params: Dict[str, Any]) -> List[Dict[str, Any]]:
    max_single = float(params["risk"]["single_name_max_weight"])
    band = float(params["portfolio"]["rebalance_band"])
    out = []
    for p in portfolio.get("positions", []):
        weight = safe_float(p.get("weight", 0.0), 0.0)
        if weight > max_single + band:
            out.append({"symbol": p.get("symbol", ""), "action": "TRIM", "reason": f"weight {weight:.2%} above limit {max_single:.2%}"})
    return out


def detect_theme_overexposure(portfolio: Dict[str, Any], params: Dict[str, Any], cycle: str = "AI_CONSOLIDATION") -> List[Dict[str, Any]]:
    target = float(params["portfolio"]["target_ai_exposure_by_cycle"].get(cycle, 0.60))
    current = sum(safe_float(p.get("weight", 0.0), 0.0) for p in portfolio.get("positions", []) if p.get("symbol") in AI_CLUSTER)
    if current > target:
        return [{"theme": "AI", "action": "REDUCE_THEME", "reason": f"AI exposure {current:.2%} > target {target:.2%}"}]
    return []


def build_portfolio_plan(portfolio: Dict[str, Any], risk: Dict[str, Any], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    params = params or STRATEGY_PARAMS
    cycle = risk.get("ai_cycle", "AI_CONSOLIDATION") if isinstance(risk, dict) else "AI_CONSOLIDATION"
    rebalance = detect_overweight_positions(portfolio, params)
    exposure = detect_theme_overexposure(portfolio, params, cycle)
    return {
        "rebalance_actions": rebalance,
        "exposure_hints": exposure,
        "target_weights": params["portfolio"]["target_ai_exposure_by_cycle"],
        "rebalance_required": bool(rebalance or exposure),
    }
