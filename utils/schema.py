from __future__ import annotations

def validate_quote_map(quote_map: dict) -> bool:
    return isinstance(quote_map, dict)

def validate_candle_map(candle_map: dict) -> bool:
    return isinstance(candle_map, dict)

def validate_portfolio(portfolio: dict) -> bool:
    return isinstance(portfolio, dict) and "positions" in portfolio and "cash" in portfolio and "portfolio_value" in portfolio
