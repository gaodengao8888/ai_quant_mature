# BASELINE

- Current baseline: v3.0.0-first-runnable
- Source baseline: ai_quant_v2_5_4_longbridge
- Protection target: do not overwrite the real-time main chain or backtest chain with simplified stand-alone scripts.
- Official real-time chain:
  lambda_function -> scheduler_event_router -> market_clock -> market_data_engine -> portfolio_sync -> ai_cycle_engine -> market_regime_engine_v2 -> signal_engine_v1 -> signal_filter_v1 -> risk_engine_v2 -> portfolio_engine -> position_engine_v2 -> risk_guard -> trader_lambda -> order_executor_longbridge -> analyzer_lambda_cn
- Official backtest chain:
  historical_data_engine -> backtest_runner -> ai_cycle_engine -> market_regime_engine_v2 -> signal_engine_v1 -> signal_filter_v1 -> risk_engine_v2 -> portfolio_engine -> position_engine_v2 -> execution_simulator -> performance_analyzer
