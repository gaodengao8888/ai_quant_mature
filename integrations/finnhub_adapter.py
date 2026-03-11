from __future__ import annotations
import json, os, time, urllib.parse, urllib.request
from typing import Dict, Any, List

API_KEY = os.getenv("FINNHUB_API_KEY", "")
API_BASE = os.getenv("FINNHUB_BASE_URL", "https://finnhub.io/api/v1")


def _http_get_json(path: str, params: Dict[str, Any], timeout: float = 4.0) -> Dict[str, Any]:
    query = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{path}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "AI-Quant-v3"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def available() -> bool:
    return bool(API_KEY)


def fetch_quote(symbol: str) -> Dict[str, Any]:
    data = _http_get_json("quote", {"symbol": symbol, "token": API_KEY}, 3.5)
    price = float(data.get("c") or 0)
    if price <= 0:
        raise ValueError(f"invalid finnhub quote for {symbol}")
    prev_close = float(data.get("pc") or 0)
    return {
        "symbol": symbol,
        "price": round(price, 2),
        "change": round(price - prev_close, 2) if prev_close > 0 else 0.0,
        "change_pct": round(((price - prev_close) / prev_close) * 100, 2) if prev_close > 0 else 0.0,
        "volume": 0.0,
        "open": float(data.get("o") or price),
        "high": float(data.get("h") or price),
        "low": float(data.get("l") or price),
        "prev_close": round(prev_close, 2),
        "timestamp": int(data.get("t") or time.time()),
    }


def fetch_candles(symbol: str, count: int = 120) -> List[Dict[str, Any]]:
    now_ts = int(time.time())
    from_ts = now_ts - 220 * 24 * 3600
    data = _http_get_json(
        "stock/candle",
        {"symbol": symbol, "resolution": "D", "from": from_ts, "to": now_ts, "token": API_KEY},
        4.5,
    )
    if data.get("s") != "ok":
        raise ValueError(f"candle status not ok for {symbol}: {data.get('s')}")
    out: List[Dict[str, Any]] = []
    for t, o, h, l, c, v in zip(data.get("t", []), data.get("o", []), data.get("h", []), data.get("l", []), data.get("c", []), data.get("v", [])):
        if float(c or 0) <= 0:
            continue
        out.append({
            "timestamp": int(t),
            "open": round(float(o), 2),
            "high": round(float(h), 2),
            "low": round(float(l), 2),
            "close": round(float(c), 2),
            "volume": float(v or 0),
        })
    if len(out) < 60:
        raise ValueError(f"not enough candles for {symbol}: {len(out)}")
    return out[-count:]
