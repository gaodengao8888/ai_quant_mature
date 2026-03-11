from __future__ import annotations
SUPPORTED_MODES = {"premarket", "market", "postmarket", "backtest", "validate"}

def normalize_mode(event: dict) -> str:
    raw = str((event or {}).get("mode", "market")).strip().lower()
    alias = {"pre":"premarket","intraday":"market","open":"market","post":"postmarket","bt":"backtest"}
    return alias.get(raw, raw)

def route_event(event: dict) -> str:
    mode = normalize_mode(event)
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    return mode
