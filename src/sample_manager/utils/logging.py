import logging
from pathlib import Path

LOG_FILE = Path("sample_manager.log")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )


def get_logger(name: str):
    return logging.getLogger(name)
