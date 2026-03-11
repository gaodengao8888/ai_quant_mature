from __future__ import annotations
from typing import Dict, Any


def get_system_params() -> Dict[str, Any]:
    return {
        "engine_name": "AI Quant Trading System",
        "param_version": "v3.1.0",
        "default_mode": "SIMULATE",
        "enable_live_trading": False,
        "market": "US",
        "base_currency": "USD",
    }


def get_universe_params() -> Dict[str, Any]:
    return {
        "core_ai_symbols": ["NVDA", "SOXX", "AVGO", "MSFT", "GOOGL", "META", "AMD", "TSM", "ANET"],
        "market_regime_symbols": ["QQQ", "SOXX", "IVV", "NVDA"],
        "default_trade_symbols": ["NVDA", "SOXX", "AVGO", "MSFT", "GOOGL", "META", "ANET", "TSLA", "IVV", "SCHD", "JNJ", "MUFG", "QQQ"],
        "max_symbol_count": 30,
    }


def get_ai_cycle_params() -> Dict[str, Any]:
    return {
        "trend_ma_fast": 20,
        "trend_ma_slow": 50,
        "long_trend_ma": 200,
        "momentum_lookback_days": 60,
        "breadth_ma_window": 50,
        "trend_score_weight": 0.30,
        "momentum_score_weight": 0.30,
        "breadth_score_weight": 0.25,
        "liquidity_score_weight": 0.15,
        "expansion_threshold": 60,
        "consolidation_threshold": 30,
        "euphoria_threshold": 10,
        "cycle_state_multipliers": {
            "AI_EXPANSION": 1.20,
            "AI_CONSOLIDATION": 1.00,
            "AI_EUPHORIA": 0.70,
            "AI_RISK_OFF": 0.00,
        },
    }


def get_market_regime_params() -> Dict[str, Any]:
    return {
        "ma_fast": 20,
        "ma_slow": 50,
        "bull_score_threshold": 25,
        "sideways_score_threshold": 0,
        "bear_score_threshold": -20,
        "regime_multipliers": {
            "BULL": 1.20,
            "SIDEWAYS": 1.00,
            "BEAR": 0.60,
            "RISK_OFF": 0.00,
        },
    }


def get_signal_params() -> Dict[str, Any]:
    return {
        "breakout_lookback": 20,
        "pullback_band": 0.03,
        "min_confidence": 0.60,
        "trend_ma_fast": 20,
        "trend_ma_slow": 50,
        "signal_types": ["BREAKOUT_BUY", "PULLBACK_BUY", "WATCH", "REDUCE", "EXIT"],
    }


def get_filter_params() -> Dict[str, Any]:
    return {
        "max_volatility_5d_avg_range": 0.08,
        "allow_breakout_in_ai_expansion": True,
        "allow_breakout_in_ai_consolidation": False,
        "allow_breakout_in_ai_euphoria": False,
        "allow_breakout_in_ai_risk_off": False,
        "allow_pullback_in_ai_expansion": True,
        "allow_pullback_in_ai_consolidation": True,
        "allow_pullback_in_ai_euphoria": True,
        "allow_pullback_in_ai_risk_off": False,
        "allow_breakout_in_bull": True,
        "allow_breakout_in_sideways": True,
        "allow_breakout_in_bear": False,
        "allow_breakout_in_market_risk_off": False,
        "allow_pullback_in_bull": True,
        "allow_pullback_in_sideways": True,
        "allow_pullback_in_bear": False,
        "allow_pullback_in_market_risk_off": False,
    }


def get_risk_params() -> Dict[str, Any]:
    return {
        "ai_cluster_max_weight": 0.70,
        "ai_cluster_caution_weight": 0.55,
        "single_name_max_weight": 0.25,
        "single_name_max_weight_crowded": 0.15,
        "overcrowded_signal_threshold": 8,
        "overcrowded_signal_warning_threshold": 6,
        "high_chase_multiple_of_ma50": 1.25,
        "correlation_alert_threshold": 0.80,
        "max_drawdown_caution": 0.10,
        "max_drawdown_alert": 0.20,
        "daily_loss_guard": 0.03,
        "risk_score_safe_max": 29,
        "risk_score_caution_max": 60,
        "risk_multipliers": {
            "SAFE": 1.00,
            "CAUTION": 0.70,
            "ALERT": 0.00,
            "RISK_STOP": 0.00,
        },
        "crowding_multipliers": {
            "LOW": 1.00,
            "MEDIUM": 0.85,
            "HIGH": 0.60,
            "EXTREME": 0.00,
        },
    }


def get_portfolio_params() -> Dict[str, Any]:
    return {
        "target_ai_exposure_by_cycle": {
            "AI_EXPANSION": 0.80,
            "AI_CONSOLIDATION": 0.60,
            "AI_EUPHORIA": 0.40,
            "AI_RISK_OFF": 0.20,
        },
        "rebalance_band": 0.05,
        "trim_threshold": 0.03,
        "allow_rebalance_under_alert": False,
    }


def get_position_params() -> Dict[str, Any]:
    return {
        "base_order_budget": 2000.0,
        "max_order_value": 3000.0,
        "min_cash_buffer_ratio": 0.20,
        "min_shares_required": 1,
        "max_new_positions_per_day": 3,
        "cash_multiplier_bands": {
            "ample": 1.00,
            "tight": 0.70,
            "very_tight": 0.30,
            "none": 0.00,
        },
    }


def get_execution_params() -> Dict[str, Any]:
    return {
        "default_mode": "SIMULATE",
        "allow_live_order_submit": False,
        "max_trades_per_day": 3,
        "max_same_symbol_buy_per_day": 1,
        "require_idempotency_check": True,
        "require_cash_check": True,
        "require_order_limit_check": True,
    }


def get_backtest_params() -> Dict[str, Any]:
    return {
        "initial_capital": 100000.0,
        "fee_rate": 0.001,
        "slippage_bps": 10,
        "execution_rule": "T+1_OPEN",
        "annual_trading_days": 252,
        "train_start": "2015-01-01",
        "train_end": "2021-12-31",
        "validate_start": "2022-01-01",
        "validate_end": "2023-12-31",
        "oos_start": "2024-01-01",
        "oos_end": "2099-12-31",
    }


def get_strategy_params() -> Dict[str, Any]:
    return {
        "system": get_system_params(),
        "universe": get_universe_params(),
        "ai_cycle": get_ai_cycle_params(),
        "market_regime": get_market_regime_params(),
        "signal": get_signal_params(),
        "filtering": get_filter_params(),
        "risk": get_risk_params(),
        "portfolio": get_portfolio_params(),
        "position": get_position_params(),
        "execution": get_execution_params(),
        "backtest": get_backtest_params(),
    }


STRATEGY_PARAMS = get_strategy_params()
