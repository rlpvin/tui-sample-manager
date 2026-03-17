import sqlite3

import pytest


@pytest.fixture(autouse=True)
def test_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    import sample_manager.db.connection as db_conn

    # Reset internal state to ensure fresh start
    monkeypatch.setattr(db_conn, "_connection", conn)

    # Also patch anywhere get_connection might have been imported
    import sample_manager.db.init_db as db_init
    import sample_manager.db.migrate as db_migrate

    monkeypatch.setattr(db_init, "get_connection", lambda: conn)
    monkeypatch.setattr(db_migrate, "get_connection", lambda: conn)
    monkeypatch.setattr(db_conn, "get_connection", lambda: conn)

    # Initialize and migrate the in-memory database
    db_init.initialize_database()
    db_migrate.run_migrations()

    yield conn
    conn.close()
