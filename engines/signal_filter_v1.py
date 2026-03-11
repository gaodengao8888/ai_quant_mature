from __future__ import annotations
from typing import Dict, Any, List
from config.strategy_params import STRATEGY_PARAMS


def filter_signals(raw_signal_payload, ai_cycle, market_regime, quote_map, candle_map, params=None):
    params = params or STRATEGY_PARAMS
    raw_signals = raw_signal_payload.get("signals", raw_signal_payload if isinstance(raw_signal_payload, list) else [])
    passed, rejected = [], []
    regime_name = market_regime.get("market_regime", "SIDEWAYS")
    cycle_name = ai_cycle.get("ai_cycle", "AI_CONSOLIDATION")
    max_vol = float(params["filtering"]["max_volatility_5d_avg_range"])
    for s in raw_signals:
        sig = s.get("signal", "WATCH")
        vol = float(s.get("volatility_ratio", 0.0))
        reason = None
        if sig == "WATCH":
            reason = "watch signal"
        elif cycle_name == "AI_RISK_OFF" and sig in ("BREAKOUT_BUY", "PULLBACK_BUY"):
            reason = "AI risk-off blocks buying"
        elif cycle_name == "AI_EUPHORIA" and sig == "BREAKOUT_BUY":
            reason = "AI euphoria blocks breakout chase"
        elif cycle_name == "AI_CONSOLIDATION" and sig == "BREAKOUT_BUY" and not params["filtering"]["allow_breakout_in_ai_consolidation"]:
            reason = "AI consolidation blocks breakout"
        elif regime_name == "RISK_OFF" and sig in ("BREAKOUT_BUY", "PULLBACK_BUY"):
            reason = "market risk-off blocks buying"
        elif regime_name == "BEAR" and sig == "BREAKOUT_BUY":
            reason = "bear regime blocks breakout"
        elif vol > max_vol:
            reason = f"volatility too high: {vol:.2%}"
        if reason:
            item = dict(s)
            item["passed"] = False
            item["block_reason"] = reason
            rejected.append(item)
        else:
            item = dict(s)
            item["passed"] = True
            item["reason"] = "passed all filters"
            passed.append(item)
    return {"passed": passed, "rejected": rejected, "passed_count": len(passed), "rejected_count": len(rejected), "regime": regime_name, "ai_cycle": cycle_name}
