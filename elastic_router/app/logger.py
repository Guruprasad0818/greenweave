"""
GreenWeave — Elastic Router
Logger: Structured logging (mirrors grid_monitor pattern)
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # avoid duplicate handlers on re-import

    logger.setLevel(logging.DEBUG)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
