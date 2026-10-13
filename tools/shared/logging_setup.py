"""Minimal shared logging setup for the MCP search-tool servers"""

from __future__ import annotations

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / ".logs"


def get_logger(tool_name: str) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"onboarding_agent.{tool_name}")
    if not logger.handlers:  # avoid duplicate handlers if called more than once
        handler = logging.FileHandler(LOG_DIR / f"{tool_name}.log")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # never bubble up to stdout/stderr by default
    return logger
