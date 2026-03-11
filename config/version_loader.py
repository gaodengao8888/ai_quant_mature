from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

def load_version_info() -> Dict[str, Any]:
    path = Path(__file__).resolve().parent.parent / "governance" / "VERSION.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
