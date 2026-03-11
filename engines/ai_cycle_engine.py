from __future__ import annotations
from typing import Dict, Any, List
from config.strategy_params import STRATEGY_PARAMS
from utils.math_utils import safe_div


def _closes(candles: List[Dict[str, Any]]) -> List[float]:
    return [float(x["close"]) for x in candles if "close" in x]


def _ma(values: List[float], n: int) -> float:
    if not values:
        return 0.0
    subset = values[-n:] if len(values) >= n else values
    return sum(subset) / len(subset)


def evaluate_ai_cycle(quote_map: Dict[str, Any], candle_map: Dict[str, Any], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    params = params or STRATEGY_PARAMS
    core = params["universe"]["core_ai_symbols"]
    trend_scores = []
    momentum_scores = []
    breadth_hits = 0
    total = 0
    for symbol in core:
        candles = candle_map.get(symbol, [])
        closes = _closes(candles)
        if len(closes) < 50:
            continue
        total += 1
        last = closes[-1]
        ma20 = _ma(closes, 20)
        ma50 = _ma(closes, 50)
        if last > ma20 > ma50:
            trend_scores.append(100)
        elif last > ma50:
            trend_scores.append(60)
        elif last > ma20:
            trend_scores.append(40)
        else:
            trend_scores.append(10)
        if len(closes) >= 60:
            ret60 = safe_div(last - closes[-60], closes[-60], 0.0)
            if ret60 > 0.40:
                momentum_scores.append(100)
            elif ret60 > 0.20:
                momentum_scores.append(70)
            elif ret60 > 0:
                momentum_scores.append(45)
            else:
                momentum_scores.append(10)
        if last > ma50:
            breadth_hits += 1
    if total == 0:
        score = 30.0
        cycle = "AI_CONSOLIDATION"
        return {"ai_cycle": cycle, "score": score, "trend_score": 0.0, "momentum_score": 0.0, "breadth_score": 0.0, "liquidity_score": 30.0}
    trend_score = sum(trend_scores) / len(trend_scores)
    momentum_score = sum(momentum_scores) / len(momentum_scores) if momentum_scores else 30.0
    breadth_ratio = breadth_hits / total
    breadth_score = breadth_ratio * 100.0
    liquid_score = 55.0 if breadth_ratio > 0.5 else 35.0
    weights = params["ai_cycle"]
    score = (
        trend_score * weights["trend_score_weight"] +
        momentum_score * weights["momentum_score_weight"] +
        breadth_score * weights["breadth_score_weight"] +
        liquid_score * weights["liquidity_score_weight"]
    )
    if score >= weights["expansion_threshold"]:
        cycle = "AI_EXPANSION"
    elif score >= weights["consolidation_threshold"]:
        cycle = "AI_CONSOLIDATION"
    elif score >= weights["euphoria_threshold"]:
        cycle = "AI_EUPHORIA"
    else:
        cycle = "AI_RISK_OFF"
    return {
        "ai_cycle": cycle,
        "score": round(score, 2),
        "trend_score": round(trend_score, 2),
        "momentum_score": round(momentum_score, 2),
        "breadth_score": round(breadth_score, 2),
        "liquidity_score": round(liquid_score, 2),
    }
