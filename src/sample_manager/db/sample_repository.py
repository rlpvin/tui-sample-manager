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

    cursor.execute(
        """
        SELECT 
            s.*, 
            GROUP_CONCAT(t.name, ', ') as tags,
            r.rating
        FROM samples s
        LEFT JOIN sample_tags st ON s.id = st.sample_id
        LEFT JOIN tags t ON st.tag_id = t.id
        LEFT JOIN ratings r ON s.id = r.sample_id
        GROUP BY s.id
        """
    )
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
        SELECT 
            s.*, 
            GROUP_CONCAT(t.name, ', ') as tags,
            r.rating
        FROM samples s
        LEFT JOIN sample_tags st ON s.id = st.sample_id
        LEFT JOIN tags t ON st.tag_id = t.id
        LEFT JOIN ratings r ON s.id = r.sample_id
        WHERE s.filename LIKE ? OR s.extension LIKE ? OR t.name LIKE ?
        GROUP BY s.id
        """,
        (like_query, like_query, like_query),
    )
    return cursor.fetchall()


def get_sample_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM samples")
    return cursor.fetchone()[0]
