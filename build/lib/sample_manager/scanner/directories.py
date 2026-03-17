from pathlib import Path

from sample_manager.db.connection import get_connection


def register_directory(path: str):
    """
    Register a sample directory for scanning.
    """

    p = Path(path).expanduser().resolve()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO sample_directories (path)
        VALUES (?)
        """,
        (str(p),),
    )

    conn.commit()


def get_registered_directories():
    """
    Return all registered sample directories.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT path FROM sample_directories
        ORDER BY path
        """)

    rows = cursor.fetchall()

    # Convert rows to simple list of paths
    return [row[0] for row in rows]


def remove_directory(path: str):
    """
    Remove a registered sample directory.
    """

    p = Path(path).expanduser().resolve()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM sample_directories
        WHERE path = ?
        """,
        (str(p),),
    )

    if cursor.rowcount == 0:

        raise ValueError("Directory not found")

    conn.commit()
