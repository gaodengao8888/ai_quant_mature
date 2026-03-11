from __future__ import annotations
from config.strategy_params import STRATEGY_PARAMS
from data.historical_data_engine import load_historical_data, slice_historical_window
from engines.ai_cycle_engine import evaluate_ai_cycle
from engines.market_regime_engine_v2 import evaluate_market_regime
from engines.signal_engine_v1 import generate_signals
from engines.signal_filter_v1 import filter_signals
from engines.risk_engine_v2 import evaluate_risk
from engines.portfolio_engine import build_portfolio_plan
from engines.position_engine_v2 import calculate_positions
from backtest.execution_simulator import simulate_execution
from backtest.performance_analyzer import analyze_performance


def _build_initial_state(config, params):
    capital = float(config.get("initial_capital", params["backtest"]["initial_capital"]))
    return {"cash": capital, "portfolio_value": capital, "positions": [], "trade_log": [], "daily_equity": []}


def _portfolio_from_state(state):
    total = float(state.get("portfolio_value", 0.0))
    positions = []
    for p in state.get("positions", []):
        item = dict(p)
        item["weight"] = round(item.get("value", 0.0) / total, 4) if total > 0 else 0.0
        positions.append(item)
    return {"positions": positions, "cash": state["cash"], "portfolio_value": state["portfolio_value"], "weights": {p['symbol']: p['weight'] for p in positions}}


def run_backtest_for_day(state, current_ts, daily_data, params):
    quote_map = daily_data["quote_map"]
    candle_map = daily_data["candle_map"]
    ai_cycle = evaluate_ai_cycle(quote_map, candle_map, params)
    regime = evaluate_market_regime(quote_map, candle_map, params)
    raw_signals = generate_signals(candle_map, regime, params)
    filtered_signals = filter_signals(raw_signals, ai_cycle, regime, quote_map, candle_map, params)
    portfolio = _portfolio_from_state(state)
    risk = evaluate_risk(portfolio, filtered_signals, ai_cycle, regime, params)
    _ = build_portfolio_plan(portfolio, risk, params)
    position_plan = calculate_positions(filtered_signals, portfolio, risk, ai_cycle, regime, params)
    execution_result = simulate_execution(position_plan, quote_map, portfolio, params)
    state["cash"] = execution_result["portfolio"]["cash"]
    state["positions"] = execution_result["portfolio"]["positions"]
    state["portfolio_value"] = execution_result["portfolio"]["portfolio_value"]
    state["trade_log"].extend(execution_result["trades"])
    state["daily_equity"].append({"timestamp": current_ts, "equity": state["portfolio_value"]})
    return state


def run_backtest(config):
    params = STRATEGY_PARAMS
    symbols = config.get("symbols", ["NVDA", "SOXX", "AVGO"])
    start = config.get("start", params["backtest"]["train_start"])
    end = config.get("end", params["backtest"]["validate_end"])
    historical = load_historical_data(symbols, start, end)
    all_ts = sorted({c["timestamp"] for candles in historical["candle_map"].values() for c in candles})
    state = _build_initial_state(config, params)
    for current_ts in all_ts:
        daily_data = slice_historical_window(historical, current_ts)
        state = run_backtest_for_day(state, current_ts, daily_data, params)
    performance = analyze_performance({"trade_log": state["trade_log"], "daily_equity": state["daily_equity"]}, params)
    return {"trade_log": state["trade_log"], "daily_equity": state["daily_equity"], "summary": performance}
