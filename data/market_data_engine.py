from __future__ import annotations
import math, os, random, time
from typing import Dict, Any, List, Tuple
from config.strategy_params import STRATEGY_PARAMS
from integrations.longbridge_adapter import longport_available, fetch_quotes as lb_fetch_quotes, fetch_candles as lb_fetch_candles
from integrations.finnhub_adapter import available as finnhub_available, fetch_quote as fh_fetch_quote, fetch_candles as fh_fetch_candles

MOCK_QUOTES = {
    "NVDA": 185.60, "SOXX": 362.10, "AVGO": 348.80, "MSFT": 434.00, "META": 703.70,
    "GOOGL": 182.70, "ANET": 149.50, "TSLA": 422.90, "IVV": 726.10, "SCHD": 33.20,
    "JNJ": 259.00, "MUFG": 18.40, "QQQ": 545.90,
}
TREND_MAP = {
    "NVDA": 0.0008, "SOXX": 0.0006, "AVGO": 0.0005, "MSFT": 0.0004, "META": 0.0009,
    "GOOGL": 0.0003, "ANET": 0.0006, "TSLA": 0.0005, "IVV": 0.0004, "SCHD": 0.0002,
    "JNJ": 0.0001, "MUFG": 0.0002, "QQQ": 0.0004,
}
PREFERRED_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "LONGPORT").upper()


def _mock_quote(symbol: str) -> Dict[str, Any]:
    price = round(float(MOCK_QUOTES.get(symbol.upper(), 100.0)), 2)
    return {
        "symbol": symbol,
        "price": price,
        "change": 0.0,
        "change_pct": 0.0,
        "volume": 1000000.0,
        "open": price,
        "high": price,
        "low": price,
        "prev_close": price,
        "timestamp": int(time.time()),
    }


def _mock_candles(symbol: str, count: int = 120, anchor_price: float | None = None) -> List[Dict[str, Any]]:
    seed = sum(ord(c) for c in symbol) + count
    rng = random.Random(seed)
    base = float(anchor_price or MOCK_QUOTES.get(symbol.upper(), 100.0))
    px = base * 0.93
    out = []
    trend = TREND_MAP.get(symbol.upper(), 0.0003)
    now_ts = int(time.time())
    for i in range(count):
        noise = rng.uniform(-0.018, 0.018)
        cycle = 0.010 * math.sin(i / 7.0)
        shock = -0.030 if i in (count // 3, count // 2) else 0.0
        ret = trend + noise + cycle + shock
        px = max(1.0, px * (1.0 + ret))
        out.append({
            "timestamp": now_ts - (count - i) * 86400,
            "open": round(px * 0.99, 2),
            "high": round(px * 1.01, 2),
            "low": round(px * 0.98, 2),
            "close": round(px, 2),
            "volume": 1000000.0 + i * 1000,
        })
    out[-1]["close"] = round(base, 2)
    return out


def _try_live_quote(symbol: str) -> Tuple[Dict[str, Any], str, str]:
    errors = []
    if PREFERRED_PROVIDER == "LONGPORT":
        if longport_available():
            try:
                rows = lb_fetch_quotes([symbol])
                if rows and rows[0].get("price", 0) > 0:
                    row = dict(rows[0])
                    row.setdefault("change", 0.0)
                    row.setdefault("change_pct", 0.0)
                    row.setdefault("volume", 0.0)
                    row.setdefault("timestamp", int(time.time()))
                    return row, "LONGPORT", ""
            except Exception as exc:
                errors.append(f"LONGPORT:{exc}")
        if finnhub_available():
            try:
                return fh_fetch_quote(symbol), "FINNHUB", " | ".join(errors)
            except Exception as exc:
                errors.append(f"FINNHUB:{exc}")
    else:
        if finnhub_available():
            try:
                return fh_fetch_quote(symbol), "FINNHUB", ""
            except Exception as exc:
                errors.append(f"FINNHUB:{exc}")
        if longport_available():
            try:
                rows = lb_fetch_quotes([symbol])
                row = dict(rows[0])
                row.setdefault("change", 0.0)
                row.setdefault("change_pct", 0.0)
                row.setdefault("volume", 0.0)
                row.setdefault("timestamp", int(time.time()))
                return row, "LONGPORT", " | ".join(errors)
            except Exception as exc:
                errors.append(f"LONGPORT:{exc}")
    raise ValueError(" | ".join(errors) if errors else f"no live quote provider for {symbol}")


def _try_live_candles(symbol: str, count: int) -> Tuple[List[Dict[str, Any]], str, str]:
    errors = []
    if PREFERRED_PROVIDER == "LONGPORT":
        if longport_available():
            try:
                closes = lb_fetch_candles(symbol, count=count)
                rows = []
                ts = int(time.time()) - count * 86400
                prev = closes[0]
                for i, close in enumerate(closes):
                    rows.append({
                        "timestamp": ts + i * 86400,
                        "open": round(prev, 2),
                        "high": round(max(prev, close) * 1.01, 2),
                        "low": round(min(prev, close) * 0.99, 2),
                        "close": round(float(close), 2),
                        "volume": 0.0,
                    })
                    prev = close
                return rows, "LONGPORT", ""
            except Exception as exc:
                errors.append(f"LONGPORT:{exc}")
        if finnhub_available():
            try:
                return fh_fetch_candles(symbol, count=count), "FINNHUB", " | ".join(errors)
            except Exception as exc:
                errors.append(f"FINNHUB:{exc}")
    else:
        if finnhub_available():
            try:
                return fh_fetch_candles(symbol, count=count), "FINNHUB", ""
            except Exception as exc:
                errors.append(f"FINNHUB:{exc}")
        if longport_available():
            try:
                closes = lb_fetch_candles(symbol, count=count)
                rows = []
                ts = int(time.time()) - count * 86400
                prev = closes[0]
                for i, close in enumerate(closes):
                    rows.append({
                        "timestamp": ts + i * 86400,
                        "open": round(prev, 2),
                        "high": round(max(prev, close) * 1.01, 2),
                        "low": round(min(prev, close) * 0.99, 2),
                        "close": round(float(close), 2),
                        "volume": 0.0,
                    })
                    prev = close
                return rows, "LONGPORT", " | ".join(errors)
            except Exception as exc:
                errors.append(f"LONGPORT:{exc}")
    raise ValueError(" | ".join(errors) if errors else f"no live candle provider for {symbol}")


def fetch_quotes(symbols: List[str]) -> Dict[str, Any]:
    quote_map = {}
    for symbol in symbols:
        try:
            quote, _, _ = _try_live_quote(symbol)
        except Exception:
            quote = _mock_quote(symbol)
        quote_map[symbol] = quote
    return quote_map


def fetch_candles(symbols: List[str], lookback: int = 120) -> Dict[str, Any]:
    candle_map = {}
    for symbol in symbols:
        try:
            candles, _, _ = _try_live_candles(symbol, lookback)
        except Exception:
            candles = _mock_candles(symbol, count=lookback)
        candle_map[symbol] = candles
    return candle_map


def validate_market_data(data: Dict[str, Any]) -> Dict[str, Any]:
    valid_symbols = [s for s in data.get("quote_map", {}) if s in data.get("candle_map", {}) and data["quote_map"][s].get("price") is not None]
    data["valid_symbols"] = valid_symbols
    data["valid_symbol_count"] = len(valid_symbols)
    return data


def get_market_data(event: Dict[str, Any] | None = None) -> Dict[str, Any]:
    event = event or {}
    symbols = [str(s).upper() for s in (event.get("symbols") or STRATEGY_PARAMS["universe"]["default_trade_symbols"])]
    count = int(event.get("count", 120) or 120)
    quote_map: Dict[str, Any] = {}
    candle_map: Dict[str, Any] = {}
    source_detail: Dict[str, Any] = {}
    live_quote_count = 0
    live_candle_count = 0
    provider_rollup = {"LONGPORT": 0, "FINNHUB": 0, "MOCK": 0}
    for symbol in symbols:
        quote_provider = "MOCK"
        candle_provider = "MOCK"
        quote_error = ""
        candle_error = ""
        try:
            quote, quote_provider, quote_error = _try_live_quote(symbol)
            live_quote_count += 1
            provider_rollup[quote_provider] += 1
        except Exception as exc:
            quote = _mock_quote(symbol)
            quote_error = str(exc)
            provider_rollup["MOCK"] += 1
        quote_map[symbol] = quote
        try:
            candles, candle_provider, candle_error = _try_live_candles(symbol, count)
            if candles:
                candles[-1]["close"] = quote["price"]
            live_candle_count += 1
        except Exception as exc:
            candles = _mock_candles(symbol, count=count, anchor_price=quote["price"])
            candle_error = str(exc)
            candle_provider = "MOCK"
        candle_map[symbol] = candles
        source_detail[symbol] = {
            "quote": "LIVE" if quote_provider != "MOCK" else "MOCK",
            "quote_provider": quote_provider,
            "candles": "LIVE" if candle_provider != "MOCK" else "MOCK",
            "candle_provider": candle_provider,
            "quote_error": quote_error,
            "candle_error": candle_error,
        }
    data_source = "LIVE" if live_quote_count == len(symbols) and live_candle_count == len(symbols) else "MIXED"
    if live_quote_count == 0 and live_candle_count == 0:
        data_source = "MOCK"
    return validate_market_data({
        "quote_map": quote_map,
        "candle_map": candle_map,
        "source_detail": source_detail,
        "provider_rollup": provider_rollup,
        "live_quote_count": live_quote_count,
        "live_candle_count": live_candle_count,
        "total_symbols": len(symbols),
        "data_source": data_source,
    })
