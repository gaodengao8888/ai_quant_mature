from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from core.scheduler_event_router import route_event
from config.strategy_params import STRATEGY_PARAMS
from config.version_loader import load_version_info
from utils.logger import get_logger, log_run_start, log_run_end, log_key_state
from data.market_data_engine import get_market_data
from data.portfolio_sync import sync_portfolio
from engines.ai_cycle_engine import evaluate_ai_cycle
from engines.market_regime_engine_v2 import evaluate_market_regime
from engines.signal_engine_v1 import generate_signals
from engines.signal_filter_v1 import filter_signals
from engines.risk_engine_v2 import evaluate_risk
from engines.portfolio_engine import build_portfolio_plan
from engines.position_engine_v2 import calculate_positions
from execution.risk_guard import guard_orders
from execution.trader_lambda import execute_trades
from analysis.analyzer_lambda_cn import generate_analysis
from backtest.backtest_runner import run_backtest

logger = get_logger("ai_quant")


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def build_run_context(event: Dict[str, Any], context: Optional[Any] = None) -> Dict[str, Any]:
    return {
        "run_id": f"run-{int(datetime.now(timezone.utc).timestamp())}",
        "timestamp_utc": _utc_now_iso(),
        "mode": route_event(event),
        "event": event or {},
        "aws_request_id": getattr(context, "aws_request_id", None),
    }


def _run_main_chain(ctx: Dict[str, Any], mode: str) -> Dict[str, Any]:
    params = STRATEGY_PARAMS
    market_data = get_market_data(ctx["event"])
    portfolio = sync_portfolio({"quote_map": market_data["quote_map"], "use_longbridge": True})
    ai_cycle = evaluate_ai_cycle(market_data["quote_map"], market_data["candle_map"], params)
    regime = evaluate_market_regime(market_data["quote_map"], market_data["candle_map"], params)
    raw_signals = generate_signals(market_data["candle_map"], regime, params)
    filtered_signals = filter_signals(raw_signals, ai_cycle, regime, market_data["quote_map"], market_data["candle_map"], params)
    risk = evaluate_risk(portfolio, filtered_signals, ai_cycle, regime, params)
    risk["ai_cycle"] = ai_cycle.get("ai_cycle", "AI_CONSOLIDATION")
    portfolio_plan = build_portfolio_plan(portfolio, risk, params)
    position_plan = calculate_positions(filtered_signals, portfolio, risk, ai_cycle, regime, params)
    guarded_plan = guard_orders(position_plan, portfolio, risk, params)
    trade_mode = ctx["event"].get("trade_mode") or STRATEGY_PARAMS["execution"]["default_mode"]
    trade_result = execute_trades(guarded_plan, mode=trade_mode)
    analysis = generate_analysis(portfolio, ai_cycle, regime, raw_signals, filtered_signals, risk, portfolio_plan, guarded_plan, trade_result, load_version_info())
    log_key_state(ctx["run_id"], "market_regime", regime.get("market_regime", "UNKNOWN"), logger)
    log_key_state(ctx["run_id"], "ai_cycle", ai_cycle.get("ai_cycle", "UNKNOWN"), logger)
    log_key_state(ctx["run_id"], "risk_status", risk.get("status", "UNKNOWN"), logger)
    return {
        "market_data": market_data,
        "portfolio": portfolio,
        "ai_cycle": ai_cycle,
        "market_regime": regime,
        "raw_signals": raw_signals,
        "filtered_signals": filtered_signals,
        "risk": risk,
        "portfolio_plan": portfolio_plan,
        "position_plan": guarded_plan,
        "trade_result": trade_result,
        "analysis": analysis,
    }


def run_premarket(ctx):
    return _run_main_chain(ctx, "premarket")


def run_trade_cycle(ctx):
    return _run_main_chain(ctx, "market")


def run_postmarket(ctx):
    return _run_main_chain(ctx, "postmarket")


def run_backtest_mode(ctx):
    config = ctx["event"].get("backtest_config", {})
    return run_backtest(config)


def lambda_handler(event: Dict[str, Any], context: Optional[Any] = None) -> Dict[str, Any]:
    ctx = build_run_context(event or {}, context)
    version_info = load_version_info()
    mode = ctx["mode"]
    log_run_start(ctx["run_id"], mode, version_info["version"], logger)
    try:
        if mode == "premarket":
            result = run_premarket(ctx)
        elif mode == "market":
            result = run_trade_cycle(ctx)
        elif mode == "postmarket":
            result = run_postmarket(ctx)
        elif mode in ("backtest", "validate"):
            result = run_backtest_mode(ctx)
        else:
            raise ValueError(f"Unsupported mode: {mode}")
        log_run_end(ctx["run_id"], "ok", logger)
        return {
            "engine": version_info["engine"],
            "version": version_info["version"],
            "mode": mode,
            "status": "ok",
            "run_id": ctx["run_id"],
            "timestamp_utc": ctx["timestamp_utc"],
            "result": result,
        }
    except Exception as exc:
        log_run_end(ctx["run_id"], "error", logger)
        return {
            "engine": version_info["engine"],
            "version": version_info["version"],
            "mode": mode,
            "status": "error",
            "run_id": ctx["run_id"],
            "timestamp_utc": ctx["timestamp_utc"],
            "error": str(exc),
        }
