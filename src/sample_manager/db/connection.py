import sqlite3
from pathlib import Path

from sample_manager.config import load_config

_connection = None


def get_connection():
    """Return singleton database connection."""

    global _connection

    if _connection is None:
        config = load_config()
        db_path = Path(config["database"]["path"])

        db_path.parent.mkdir(parents=True, exist_ok=True)

        _connection = sqlite3.connect(db_path)
        _connection.row_factory = sqlite3.Row

    return _connection
