import sqlite3

import pytest

from sample_manager.db import connection
from sample_manager.db.init_db import initialize_database
from sample_manager.db.migrate import run_migrations


@pytest.fixture
def test_db(monkeypatch):

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    monkeypatch.setattr(connection, "_connection", conn)

    initialize_database()
    run_migrations()

    return conn
