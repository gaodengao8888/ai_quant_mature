from __future__ import annotations
import logging

_LOGGERS = {}

def get_logger(name: str):
    if name in _LOGGERS:
        return _LOGGERS[name]
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.propagate = False
    _LOGGERS[name] = logger
    return logger

def log_run_start(run_id: str, mode: str, version: str, logger=None):
    (logger or get_logger("ai_quant")).info(f"RUN_START | run_id={run_id} | mode={mode} | version={version}")

def log_run_end(run_id: str, status: str, logger=None):
    (logger or get_logger("ai_quant")).info(f"RUN_END | run_id={run_id} | status={status}")

def log_key_state(run_id: str, key: str, value, logger=None):
    (logger or get_logger("ai_quant")).info(f"RUN_STATE | run_id={run_id} | {key}={value}")
