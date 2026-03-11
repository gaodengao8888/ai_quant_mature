from __future__ import annotations
import math
from typing import Dict, Any, List


def calculate_max_drawdown(daily_equity: List[Dict[str, Any]]) -> float:
    peak = None
    max_dd = 0.0
    for row in daily_equity:
        equity = float(row["equity"])
        if peak is None or equity > peak:
            peak = equity
        if peak and peak > 0:
            dd = (peak - equity) / peak
            max_dd = max(max_dd, dd)
    return max_dd


def _daily_returns(daily_equity: List[Dict[str, Any]]) -> List[float]:
    returns = []
    for i in range(1, len(daily_equity)):
        prev_eq = float(daily_equity[i - 1]["equity"])
        curr_eq = float(daily_equity[i]["equity"])
        if prev_eq > 0:
            returns.append((curr_eq - prev_eq) / prev_eq)
    return returns


def calculate_sharpe(daily_returns: List[float]) -> float:
    if not daily_returns:
        return 0.0
    mean_ret = sum(daily_returns) / len(daily_returns)
    variance = sum((x - mean_ret) ** 2 for x in daily_returns) / len(daily_returns)
    std = math.sqrt(variance)
    return (mean_ret / std) * math.sqrt(252) if std > 0 else 0.0


def calculate_sortino(daily_returns: List[float]) -> float:
    if not daily_returns:
        return 0.0
    mean_ret = sum(daily_returns) / len(daily_returns)
    downside = [x for x in daily_returns if x < 0]
    if not downside:
        return 0.0
    downside_var = sum(x * x for x in downside) / len(downside)
    downside_std = math.sqrt(downside_var)
    return (mean_ret / downside_std) * math.sqrt(252) if downside_std > 0 else 0.0


def calculate_calmar(annual_return: float, max_drawdown: float) -> float:
    return annual_return / max_drawdown if max_drawdown > 0 else 0.0


def analyze_performance(backtest_result: Dict[str, Any], params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    daily_equity = backtest_result.get("daily_equity", [])
    trades = backtest_result.get("trade_log", [])
    if not daily_equity:
        return {"total_return": 0.0, "annual_return": 0.0, "max_drawdown": 0.0, "sharpe": 0.0, "sortino": 0.0, "calmar": 0.0, "trade_count": 0}
    start_eq = float(daily_equity[0]["equity"])
    end_eq = float(daily_equity[-1]["equity"])
    total_return = (end_eq - start_eq) / start_eq if start_eq > 0 else 0.0
    num_days = max(1, len(daily_equity))
    annual_return = (1 + total_return) ** (252 / num_days) - 1 if num_days > 0 else 0.0
    daily_returns = _daily_returns(daily_equity)
    max_drawdown = calculate_max_drawdown(daily_equity)
    sharpe = calculate_sharpe(daily_returns)
    sortino = calculate_sortino(daily_returns)
    calmar = calculate_calmar(annual_return, max_drawdown)
    return {"total_return": total_return, "annual_return": annual_return, "max_drawdown": max_drawdown, "sharpe": sharpe, "sortino": sortino, "calmar": calmar, "trade_count": len(trades)}
