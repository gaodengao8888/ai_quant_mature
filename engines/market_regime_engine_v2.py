from __future__ import annotations
from typing import Dict, Any, List
from config.strategy_params import STRATEGY_PARAMS


def _closes(candles: List[Dict[str, Any]]) -> List[float]:
    return [float(x["close"]) for x in candles if "close" in x]


def _ma(values: List[float], n: int) -> float:
    subset = values[-n:] if len(values) >= n else values
    return sum(subset) / len(subset) if subset else 0.0


def evaluate_market_regime(quote_map: Dict[str, Any], candle_map: Dict[str, Any], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    params = params or STRATEGY_PARAMS
    regime_symbols = params["universe"]["market_regime_symbols"]
    details = []
    for symbol in regime_symbols:
        closes = _closes(candle_map.get(symbol, []))
        if len(closes) < 50:
            continue
        price = closes[-1]
        ma20 = _ma(closes, 20)
        ma50 = _ma(closes, 50)
        score = 0
        if price > ma20:
            score += 20
        else:
            score -= 20
        if ma20 > ma50:
            score += 20
        else:
            score -= 20
        if len(closes) > 5 and price > closes[-6]:
            score += 10
        details.append({"symbol": symbol, "price": round(price,2), "ma20": round(ma20,2), "ma50": round(ma50,2), "trend_score": score})
    avg_score = sum(x["trend_score"] for x in details) / len(details) if details else 0.0
    cfg = params["market_regime"]
    if avg_score >= cfg["bull_score_threshold"]:
        regime = "BULL"
    elif avg_score >= cfg["sideways_score_threshold"]:
        regime = "SIDEWAYS"
    elif avg_score >= cfg["bear_score_threshold"]:
        regime = "BEAR"
    else:
        regime = "RISK_OFF"
    return {"market_regime": regime, "score": round(avg_score,2), "detail": details, "symbols_used": [d['symbol'] for d in details]}
