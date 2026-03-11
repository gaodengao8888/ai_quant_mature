from __future__ import annotations

def get_module_registry():
    return {
        "market_data_engine":{"input":["event"],"output":["quote_map","candle_map"],"dependencies":[],"stage":"stable"},
        "portfolio_sync":{"input":["event"],"output":["portfolio"],"dependencies":[],"stage":"stable"},
        "ai_cycle_engine":{"input":["quote_map","candle_map","params"],"output":["ai_cycle"],"dependencies":[],"stage":"stable"},
        "market_regime_engine_v2":{"input":["quote_map","candle_map","params"],"output":["market_regime"],"dependencies":[],"stage":"stable"},
        "signal_engine_v1":{"input":["candle_map","market_regime","params"],"output":["raw_signals"],"dependencies":[],"stage":"stable"},
        "signal_filter_v1":{"input":["raw_signals","ai_cycle","market_regime","quote_map","candle_map","params"],"output":["filtered_signals"],"dependencies":["signal_engine_v1"],"stage":"stable"},
        "risk_engine_v2":{"input":["portfolio","filtered_signals","ai_cycle","market_regime","params"],"output":["risk_result"],"dependencies":["signal_filter_v1"],"stage":"stable"},
        "portfolio_engine":{"input":["portfolio","risk_result","params"],"output":["portfolio_plan"],"dependencies":["risk_engine_v2"],"stage":"stable"},
        "position_engine_v2":{"input":["filtered_signals","portfolio","risk_result","ai_cycle","market_regime","params"],"output":["position_plan"],"dependencies":["risk_engine_v2"],"stage":"stable"},
        "risk_guard":{"input":["position_plan","portfolio","risk_result","params"],"output":["guarded_orders"],"dependencies":["position_engine_v2"],"stage":"stable"},
        "trader_lambda":{"input":["guarded_orders","mode"],"output":["trade_result"],"dependencies":["risk_guard"],"stage":"stable"},
        "analyzer_lambda_cn":{"input":["all state objects"],"output":["analysis"],"dependencies":["trader_lambda"],"stage":"stable"},
        "backtest_runner":{"input":["config"],"output":["backtest_result"],"dependencies":[],"stage":"testing"},
    }

def validate_module_registry():
    registry = get_module_registry()
    errors = []
    for name, cfg in registry.items():
        for key in ("input","output","dependencies","stage"):
            if key not in cfg:
                errors.append(f"{name} missing key: {key}")
        for dep in cfg.get("dependencies", []):
            if dep not in registry:
                errors.append(f"{name} dependency missing: {dep}")
    return {"ok": len(errors)==0, "errors": errors, "module_count": len(registry)}
