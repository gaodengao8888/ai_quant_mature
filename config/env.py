from __future__ import annotations
import os

def get_env(name: str, default=None):
    return os.getenv(name, default)
