from __future__ import annotations

def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default

def safe_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default

def safe_div(numerator, denominator, default=0.0):
    try:
        if float(denominator) == 0:
            return default
        return float(numerator) / float(denominator)
    except Exception:
        return default

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))
