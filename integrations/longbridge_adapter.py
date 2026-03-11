import os
import sys
from pathlib import Path
from decimal import Decimal
from utils.math_utils import safe_float
from utils.response_utils import response

LONGPORT_REQUIRED_ENVS = ["LONGPORT_APP_KEY", "LONGPORT_APP_SECRET", "LONGPORT_ACCESS_TOKEN"]
SDK_IMPORT_CANDIDATES = ("longport.openapi", "longbridge.openapi")


def _normalize_symbol(symbol: str) -> str:
    s = str(symbol or "").upper().strip()
    if "." in s:
        return s.split(".", 1)[0]
    return s


def _to_longport_symbol(symbol: str, default_region: str = "US") -> str:
    s = str(symbol or "").upper().strip()
    if "." in s:
        return s
    return f"{s}.{default_region}"


def _decimal_to_float(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    return safe_float(value, default)


def longport_available() -> bool:
    return all(os.getenv(k) for k in LONGPORT_REQUIRED_ENVS)


def _candidate_paths():
    here = Path(__file__).resolve().parent
    pyver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    raw = [
        here,
        here / "vendor",
        here / "vendored",
        here / "python",
        here / "python" / "lib" / pyver / "site-packages",
        Path("/opt/python"),
        Path("/opt/python/lib") / pyver / "site-packages",
        Path("/var/task"),
        Path("/var/task/python"),
        Path("/var/task/vendor"),
        Path("/var/task/vendored"),
    ]
    out = []
    seen = set()
    for p in raw:
        s = str(p)
        if s not in seen:
            out.append(s)
            seen.add(s)
    return out


def sdk_bootstrap():
    added = []
    existing = []
    for p in _candidate_paths():
        if os.path.isdir(p):
            existing.append(p)
            if p not in sys.path:
                sys.path.insert(0, p)
                added.append(p)
    return {"added_paths": added, "existing_paths": existing}


def _import_openapi():
    bootstrap = sdk_bootstrap()
    errors = []
    for module_name in SDK_IMPORT_CANDIDATES:
        try:
            module = __import__(module_name, fromlist=["*"])
            return module, bootstrap, errors
        except Exception as exc:
            errors.append(f"{module_name}: {exc}")
    raise ImportError("unable to import Longbridge OpenAPI SDK; " + " | ".join(errors))


def sdk_diagnostics():
    sdk_ready = False
    sdk_module = ""
    sdk_error = ""
    bootstrap = sdk_bootstrap()
    try:
        module, _, errors = _import_openapi()
        sdk_ready = True
        sdk_module = getattr(module, "__name__", "")
        sdk_error = " | ".join(errors)
    except Exception as exc:
        sdk_error = str(exc)
    return response(
        "Longbridge Adapter",
        sdk_ready=sdk_ready,
        sdk_module=sdk_module,
        env_ready=longport_available(),
        missing_envs=[k for k in LONGPORT_REQUIRED_ENVS if not os.getenv(k)],
        sdk_error=sdk_error,
        searched_paths=bootstrap.get("existing_paths", []),
        added_paths=bootstrap.get("added_paths", []),
        sys_path_head=sys.path[:12],
    )


def build_config():
    openapi, _, _ = _import_openapi()
    return openapi.Config.from_env()


def fetch_quotes(symbols):
    openapi, _, _ = _import_openapi()
    config = build_config()
    ctx = openapi.QuoteContext(config)
    req_symbols = [_to_longport_symbol(s) for s in symbols]
    rows = ctx.quote(req_symbols)
    out = []
    for row in rows:
        symbol = _normalize_symbol(getattr(row, "symbol", ""))
        out.append({
            "symbol": symbol,
            "price": round(_decimal_to_float(getattr(row, "last_done", 0.0)), 2),
            "prev_close": round(_decimal_to_float(getattr(row, "prev_close", 0.0)), 2),
            "open": round(_decimal_to_float(getattr(row, "open", 0.0)), 2),
            "high": round(_decimal_to_float(getattr(row, "high", 0.0)), 2),
            "low": round(_decimal_to_float(getattr(row, "low", 0.0)), 2),
            "source": "longbridge_live",
            "quote_source": "LIVE",
        })
    return out


def fetch_candles(symbol: str, count: int = 120):
    openapi, _, _ = _import_openapi()
    config = build_config()
    ctx = openapi.QuoteContext(config)
    period = getattr(openapi.Period, "Day")
    adjust = getattr(openapi.AdjustType, "NoAdjust")
    rows = ctx.candlesticks(_to_longport_symbol(symbol), period, int(count), adjust)
    closes = [round(_decimal_to_float(getattr(x, "close", 0.0)), 2) for x in rows if _decimal_to_float(getattr(x, "close", 0.0)) > 0]
    return closes[-count:]


def fetch_account_balance(currency: str = "USD"):
    openapi, _, _ = _import_openapi()
    config = build_config()
    ctx = openapi.TradeContext(config)
    try:
        rows = ctx.account_balance(currency)
    except Exception:
        rows = ctx.account_balance()
    balances = []
    for row in rows:
        balances.append({
            "currency": getattr(row, "currency", currency),
            "total_cash": round(_decimal_to_float(getattr(row, "total_cash", 0.0)), 2),
            "net_assets": round(_decimal_to_float(getattr(row, "net_assets", 0.0)), 2),
            "buy_power": round(_decimal_to_float(getattr(row, "buy_power", 0.0)), 2),
            "cash_infos": [
                {
                    "currency": getattr(c, "currency", ""),
                    "available_cash": round(_decimal_to_float(getattr(c, "available_cash", 0.0)), 2),
                    "withdraw_cash": round(_decimal_to_float(getattr(c, "withdraw_cash", 0.0)), 2),
                    "frozen_cash": round(_decimal_to_float(getattr(c, "frozen_cash", 0.0)), 2),
                    "settling_cash": round(_decimal_to_float(getattr(c, "settling_cash", 0.0)), 2),
                }
                for c in getattr(row, "cash_infos", [])
            ],
        })
    return balances


def fetch_stock_positions(symbols=None):
    openapi, _, _ = _import_openapi()
    config = build_config()
    ctx = openapi.TradeContext(config)
    req_symbols = None
    if symbols:
        req_symbols = [_to_longport_symbol(s) for s in symbols]
    resp = ctx.stock_positions(req_symbols)
    positions = []
    for channel in getattr(resp, "channels", []):
        for pos in getattr(channel, "positions", []):
            positions.append({
                "account_channel": getattr(channel, "account_channel", ""),
                "symbol": _normalize_symbol(getattr(pos, "symbol", "")),
                "raw_symbol": getattr(pos, "symbol", ""),
                "symbol_name": getattr(pos, "symbol_name", ""),
                "shares": int(_decimal_to_float(getattr(pos, "quantity", 0.0))),
                "available_quantity": int(_decimal_to_float(getattr(pos, "available_quantity", 0.0))),
                "cost": round(_decimal_to_float(getattr(pos, "cost_price", 0.0)), 4),
                "currency": getattr(pos, "currency", ""),
                "market": getattr(getattr(pos, "market", None), "__name__", str(getattr(pos, "market", ""))),
            })
    return positions


def submit_order(symbol: str, quantity: int, side: str = "BUY", order_type: str = "LO", submitted_price=None, remark: str = "AI Quant v2.5.4"):
    openapi, _, _ = _import_openapi()
    config = build_config()
    ctx = openapi.TradeContext(config)
    side_value = str(side or "BUY").upper()
    order_type_value = str(order_type or "LO").upper()
    payload = {
        "symbol": _to_longport_symbol(symbol),
        "quantity": int(quantity),
        "submitted_price": submitted_price,
        "remark": remark,
    }

    if hasattr(openapi, "OrderSide"):
        payload["side"] = getattr(openapi.OrderSide, "Buy" if side_value == "BUY" else "Sell")
    else:
        payload["side"] = side_value

    if hasattr(openapi, "OrderType"):
        payload["order_type"] = getattr(openapi.OrderType, "LO" if order_type_value == "LO" else order_type_value, order_type_value)
    else:
        payload["order_type"] = order_type_value

    if submitted_price is not None and hasattr(openapi, "Decimal"):
        payload["submitted_price"] = openapi.Decimal(str(submitted_price))

    if hasattr(openapi, "TimeInForceType"):
        payload["time_in_force"] = getattr(openapi.TimeInForceType, "Day")

    response_obj = None
    last_error = None
    for method_name in ("submit_order", "place_order"):
        if not hasattr(ctx, method_name):
            continue
        method = getattr(ctx, method_name)
        try:
            try:
                response_obj = method(**payload)
            except TypeError:
                response_obj = method(payload)
            break
        except Exception as exc:
            last_error = exc
    if response_obj is None:
        raise RuntimeError(f"Longbridge order submission failed: {last_error or 'submit_order/place_order unavailable'}")

    order_id = getattr(response_obj, "order_id", "") or getattr(response_obj, "id", "")
    return response(
        "Longbridge Adapter",
        order_id=str(order_id),
        symbol=symbol,
        quantity=int(quantity),
        side=side_value,
        order_type=order_type_value,
        submitted_price=safe_float(submitted_price, 0.0) if submitted_price is not None else None,
        raw_result=str(response_obj),
    )
