import sqlite3

import pytest


@pytest.fixture
def test_db(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        path TEXT UNIQUE,
        extension TEXT,
        size INTEGER
    );
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    CREATE TABLE IF NOT EXISTS sample_tags (
        sample_id INTEGER,
        tag_id INTEGER,
        UNIQUE(sample_id, tag_id)
    );
    CREATE TABLE IF NOT EXISTS ratings (
        sample_id INTEGER PRIMARY KEY,
        rating INTEGER
    );
    CREATE TABLE IF NOT EXISTS sample_directories (
        path TEXT PRIMARY KEY
    );
    """)
    conn.commit()

    import sample_manager.db.connection as db_conn
    monkeypatch.setattr(db_conn, "_connection", conn)
    monkeypatch.setattr(db_conn, "get_connection", lambda: conn)

    yield conn
    conn.close()
