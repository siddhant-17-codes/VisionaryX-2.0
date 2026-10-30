import logging
import os
import sys


def setup_logger(name: str) -> logging.Logger:
    """Logs go to stdout only: Render keeps stdout, while files written to its disk
    vanish on every deploy and restart. LOG_LEVEL (default INFO) sets the detail."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler)

    return logger
