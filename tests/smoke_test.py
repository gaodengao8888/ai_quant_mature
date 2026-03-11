from __future__ import annotations
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.lambda_function import lambda_handler

EVENT_MAP = {
    "premarket": "test_event_premarket.json",
    "market": "test_event_market.json",
    "postmarket": "test_event_postmarket.json",
    "backtest": "test_event_backtest.json",
}

def load_event(mode):
    tests_dir = Path(__file__).resolve().parent
    with open(tests_dir / EVENT_MAP[mode], "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "market"
    event = load_event(mode)
    result = lambda_handler(event, context=None)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
