from sample_manager.db.migrate import run_migrations


def test_migrations_are_idempotent(test_db):
    """
    Running migrations multiple times should not reapply them.
    """

    run_migrations()

    cursor = test_db.cursor()

    cursor.execute("SELECT name FROM migrations")
    migrations = cursor.fetchall()

    names = {row["name"] for row in migrations}

    assert "001_initial_schema.sql" in names
    assert "002_sample_directories.sql" in names

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    tables = {row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")}

    expected_tables = {
        "samples",
        "tags",
        "sample_tags",
        "ratings",
        "collections",
        "file_hashes",
        "migrations",
        "sample_directories",
    }

    assert tables == expected_tables
