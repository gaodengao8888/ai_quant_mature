#!/bin/bash
set -e
echo "AI Quant Project Validator"
python - <<EOF
import core, data, engines, execution, analysis, backtest, config, utils
print("Import check OK")
EOF
test -f governance/VERSION.json && echo "VERSION.json found"
test -f governance/CHANGELOG.md && echo "CHANGELOG.md found"
test -f governance/BASELINE.md && echo "BASELINE.md found"
python - <<EOF
from config.strategy_params import get_strategy_params
assert get_strategy_params()
print("strategy_params loaded")
EOF
python tests/smoke_test.py premarket >/dev/null
python tests/smoke_test.py market >/dev/null
python tests/smoke_test.py postmarket >/dev/null
python tests/smoke_test.py backtest >/dev/null
echo "Validation complete."
