from __future__ import annotations
from typing import Dict, Any, List
from data.market_data_engine import fetch_candles

def load_historical_data(symbols: List[str], start: str, end: str) -> Dict[str, Any]:
    candle_map = fetch_candles(symbols, lookback=120)
    quote_map = {s: {"symbol": s, "price": candle_map[s][-1]["close"], "timestamp": candle_map[s][-1]["timestamp"]} for s in candle_map}
    return {"candle_map": candle_map, "quote_map": quote_map}

def slice_historical_window(data: Dict[str, Any], date: int) -> Dict[str, Any]:
    candle_map = {}
    for symbol, candles in data.get("candle_map", {}).items():
        sliced = [c for c in candles if c["timestamp"] <= date]
        candle_map[symbol] = sliced
    quote_map = {}
    for symbol, candles in candle_map.items():
        if candles:
            last = candles[-1]
            quote_map[symbol] = {"symbol": symbol, "price": last["close"], "timestamp": last["timestamp"], "volume": last["volume"]}
    return {"candle_map": candle_map, "quote_map": quote_map}
