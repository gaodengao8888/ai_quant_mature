# CHANGELOG

## v3.1.0-first-runnable
### Stage
Development

### Added
- Reorganized v2.5.4 logic into v3 engineering directories: core/data/engines/execution/analysis/backtest/config/governance/utils/integrations/tests/scripts.
- Added unified real-time main chain and backtest chain.
- Added governance files VERSION/CHANGELOG/BASELINE.
- Added smoke tests for premarket/market/postmarket/backtest.
- Added Longbridge + Finnhub fallback capable market data adapter interfaces.

### Changed
- Converted v2.5.4 modules into package-based imports.
- Upgraded risk engine to v2 semantics and added portfolio plan output.
- Upgraded position engine to unified multiplier budget formula.
- Unified output schema for quote_map/candle_map/portfolio/order_plan/trade_result.

### Notes
- Default runtime remains MOCK + SIMULATE.
- Smoke tests pass locally for premarket, market, postmarket, and backtest.
- Live trading remains disabled by default.
