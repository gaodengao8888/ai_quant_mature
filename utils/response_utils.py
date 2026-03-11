from __future__ import annotations
import json
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def response(engine, status="ok", **kwargs):
    payload = {"engine": engine, "timestamp_utc": utc_now(), "status": status}
    payload.update(kwargs)
    return payload
