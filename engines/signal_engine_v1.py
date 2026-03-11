from __future__ import annotations
import statistics
from typing import Dict, Any, List
from config.strategy_params import STRATEGY_PARAMS


def _ma(prices: List[float], n: int) -> float:
    subset = prices[-n:] if len(prices) >= n else prices
    return sum(subset) / len(subset) if subset else 0.0


def _volatility_ratio(prices: List[float], n: int = 20) -> float:
    if len(prices) < n + 1:
        return 0.0
    subset = prices[-n:]
    mean_px = sum(subset) / len(subset)
    return statistics.pstdev(subset) / mean_px if mean_px > 0 else 0.0


def generate_signal_for_symbol(symbol: str, candles: List[Dict[str, Any]], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    params = params or STRATEGY_PARAMS
    closes = [float(c["close"]) for c in candles if "close" in c]
    ma_fast = int(params["signal"]["trend_ma_fast"])
    ma_slow = int(params["signal"]["trend_ma_slow"])
    lookback = int(params["signal"]["breakout_lookback"])
    pullback_band = float(params["signal"]["pullback_band"])
    if len(closes) < max(ma_slow, lookback + 1):
        return {"symbol": symbol, "signal": "WATCH", "price": closes[-1] if closes else 0.0, "confidence": 0.0, "reason": "not enough candles", "volatility_ratio": 0.0}
    price = closes[-1]
    ma20 = _ma(closes, ma_fast)
    ma50 = _ma(closes, ma_slow)
    prev_high = max(closes[-(lookback + 1):-1])
    vr = _volatility_ratio(closes, 20)
    signal = "WATCH"
    conf = 0.4
    reason = "no setup"
    if price > prev_high and price > ma20 > ma50:
        signal = "BREAKOUT_BUY"
        conf = 0.78
        reason = "close above breakout high with trend alignment"
    elif ma20 > ma50 and ma20 * (1 - pullback_band) <= price <= ma20 * (1 + pullback_band / 3):
        signal = "PULLBACK_BUY"
        conf = 0.66
        reason = "price near MA20 pullback zone"
    return {
        "symbol": symbol,
        "signal": signal,
        "price": round(price, 2),
        "confidence": round(conf, 2),
        "reason": reason,
        "ma20": round(ma20, 2),
        "ma50": round(ma50, 2),
        "prev_high": round(prev_high, 2),
        "volatility_ratio": round(vr, 4),
    }


def generate_signals(candle_map: Dict[str, Any], regime: Dict[str, Any] | None = None, params: Dict[str, Any] | None = None):
    params = params or STRATEGY_PARAMS
    signals = [generate_signal_for_symbol(symbol, candles, params) for symbol, candles in candle_map.items()]
    actionable = [s for s in signals if s["signal"] != "WATCH"]
    return {"signals": signals, "actionable_count": len(actionable)}
