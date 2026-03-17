import logging
from pathlib import Path

LOG_FILE = Path("logs/app.log")


def setup_logging():
    """Configure application logging."""

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )

    logger = logging.getLogger("sample_manager")
    return logger
