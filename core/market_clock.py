from __future__ import annotations
from datetime import datetime, timezone, timedelta

def _to_utc_datetime(now=None):
    if now is None:
        return datetime.now(timezone.utc)
    if isinstance(now, datetime):
        return now.astimezone(timezone.utc) if now.tzinfo else now.replace(tzinfo=timezone.utc)
    raise TypeError("now must be datetime or None")

def is_trading_day(now=None, market: str = "US") -> bool:
    dt = _to_utc_datetime(now)
    return dt.weekday() < 5

def get_market_phase(now=None, market: str = "US") -> str:
    dt = _to_utc_datetime(now)
    if not is_trading_day(dt, market):
        return "CLOSED"
    est = dt - timedelta(hours=5)
    hhmm = est.hour * 100 + est.minute
    if 400 <= hhmm < 930:
        return "PREMARKET"
    if 930 <= hhmm < 1600:
        return "OPEN"
    if 1600 <= hhmm < 2000:
        return "POSTMARKET"
    return "CLOSED"
