from __future__ import annotations
from typing import Dict, Any

def sync_account(event=None) -> Dict[str, Any]:
    return {"account_id":"mock-account","cash":12486.58,"buying_power":12486.58,"source":"MOCK"}

def merge_account_and_portfolio(account_info: dict, portfolio_info: dict) -> dict:
    out = dict(portfolio_info)
    out["account"] = account_info
    return out
