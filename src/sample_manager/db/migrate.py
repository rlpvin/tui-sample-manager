from pathlib import Path

from sample_manager.db.connection import get_connection

MIGRATIONS_PATH = Path(__file__).parent / "migrations"


def run_migrations():
    """Apply pending database migrations."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}

    migration_files = sorted(MIGRATIONS_PATH.glob("*.sql"))

    for migration in migration_files:
        name = migration.name

        if name in applied:
            continue

        print(f"Applying migration: {name}")

        sql = migration.read_text()

        cursor.executescript(sql)

        cursor.execute("INSERT INTO migrations (name) VALUES (?)", (name,))

    conn.commit()
