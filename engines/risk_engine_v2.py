from __future__ import annotations
from typing import Dict, Any, List
from config.strategy_params import STRATEGY_PARAMS
from utils.math_utils import safe_float

AI_CLUSTER = {"NVDA", "SOXX", "AVGO", "MSFT", "META", "GOOGL", "ANET", "TSLA", "AMD", "TSM"}


def _estimate_drawdown(portfolio: Dict[str, Any]) -> float:
    positions = portfolio.get("positions", [])
    if not positions:
        return 0.0
    pnl_sum = sum(safe_float(p.get("pnl", 0.0), 0.0) for p in positions)
    cost_sum = sum(safe_float(p.get("cost_value", 0.0), 0.0) for p in positions)
    return abs(min(0.0, pnl_sum / cost_sum)) if cost_sum > 0 else 0.0


def evaluate_risk(portfolio, filtered_signals, ai_cycle, market_regime, params=None):
    params = params or STRATEGY_PARAMS
    positions = portfolio.get("positions", [])
    passed_count = int(filtered_signals.get("passed_count", 0))
    risk_cfg = params["risk"]
    risk_score = 0
    alerts: List[str] = []
    max_single = float(risk_cfg["single_name_max_weight"])
    overweight = [p["symbol"] for p in positions if float(p.get("weight", 0.0)) > max_single]
    if overweight:
        risk_score += 25
        alerts.append(f"single-name overweight: {', '.join(overweight)}")
    ai_cluster_weight = sum(float(p.get("weight", 0.0)) for p in positions if p.get("symbol") in AI_CLUSTER)
    if ai_cluster_weight > float(risk_cfg["ai_cluster_max_weight"]):
        risk_score += 20
        alerts.append("AI cluster exposure above max")
    elif ai_cluster_weight > float(risk_cfg["ai_cluster_caution_weight"]):
        risk_score += 10
        alerts.append("AI cluster exposure elevated")
    if passed_count >= int(risk_cfg["overcrowded_signal_threshold"]):
        risk_score += 20
        alerts.append("crowded signal day")
        crowding = "HIGH"
    elif passed_count >= int(risk_cfg["overcrowded_signal_warning_threshold"]):
        risk_score += 10
        alerts.append("moderate crowding")
        crowding = "MEDIUM"
    else:
        crowding = "LOW"
    regime_name = market_regime.get("market_regime", "SIDEWAYS")
    if regime_name == "RISK_OFF":
        risk_score += 40
        alerts.append("market regime risk-off")
    elif regime_name == "BEAR":
        risk_score += 20
        alerts.append("market regime bear")
    elif regime_name == "SIDEWAYS":
        risk_score += 8
    cycle_name = ai_cycle.get("ai_cycle", "AI_CONSOLIDATION")
    if cycle_name == "AI_RISK_OFF":
        risk_score += 40
        alerts.append("AI cycle risk-off")
    elif cycle_name == "AI_EUPHORIA":
        risk_score += 12
        alerts.append("AI cycle euphoric")
    drawdown = _estimate_drawdown(portfolio)
    if drawdown >= float(risk_cfg["max_drawdown_alert"]):
        risk_score += 25
        alerts.append("portfolio drawdown alert")
    elif drawdown >= float(risk_cfg["max_drawdown_caution"]):
        risk_score += 12
        alerts.append("portfolio drawdown caution")
    if risk_score >= 80:
        status = "RISK_STOP"
    elif risk_score > float(risk_cfg["risk_score_caution_max"]):
        status = "ALERT"
    elif risk_score > float(risk_cfg["risk_score_safe_max"]):
        status = "CAUTION"
    else:
        status = "SAFE"
    return {
        "status": status,
        "risk_score": int(risk_score),
        "alerts": alerts,
        "ai_exposure": round(ai_cluster_weight, 4),
        "crowding": crowding,
        "drawdown": round(-drawdown, 4),
    }
