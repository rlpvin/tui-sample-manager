import os
import logging
from pathlib import Path

LOG_FILE = Path("sample_manager.log")


def setup_logging():
    # Allow log level to be configured via environment variable
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    handlers = [logging.FileHandler(LOG_FILE)]
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        handlers=handlers,
    )


def get_logger(name: str):
    return logging.getLogger(name)
