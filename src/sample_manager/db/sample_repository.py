from sample_manager.db.connection import get_connection


def create_sample(path, filename, extension, size):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO samples (path, filename, extension, size)
        VALUES (?, ?, ?, ?)
        """,
        (path, filename, extension, size),
    )

    conn.commit()


def get_sample_by_id(sample_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM samples WHERE id=?", (sample_id,))
    return cursor.fetchone()


def get_all_samples():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM samples")
    return cursor.fetchall()


def delete_sample(sample_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM samples WHERE id=?", (sample_id,))
    conn.commit()


def bulk_create_samples(samples_list):
    conn = get_connection()
    cursor = conn.cursor()
    
    data_to_insert = [
        (s["path"], s["filename"], s["extension"], s["size"])
        for s in samples_list
    ]
    
    cursor.executemany(
        """
        INSERT INTO samples (path, filename, extension, size)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            size = excluded.size,
            filename = excluded.filename
        """,
        data_to_insert
    )
    conn.commit()

def search_samples(query):

    conn = get_connection()
    cursor = conn.cursor()

    # Use parameterized query to prevent SQL injection
    like_query = f"%{query}%"
    cursor.execute(
        """
        SELECT * FROM samples 
        WHERE filename LIKE ? OR extension LIKE ?
        """,
        (like_query, like_query),
    )
    return cursor.fetchall()


def get_sample_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM samples")
    return cursor.fetchone()[0]
