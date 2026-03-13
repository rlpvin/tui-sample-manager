from sample_manager.db.connection import get_connection


def register_directory(path: str):
    """Register a directory for scanning."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO sample_directories (path)
        VALUES (?)
        """,
        (path,),
    )

    conn.commit()


def get_registered_directories():
    """Return all registered directories."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT path FROM sample_directories")

    return [row["path"] for row in cursor.fetchall()]