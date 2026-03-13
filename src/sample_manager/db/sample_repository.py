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
    """
    samples_list should be a list of tuples: 
    [(path, filename, extension, size), ...]
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # executemany is significantly faster than a loop
    cursor.executemany(
        """
        INSERT OR IGNORE INTO samples (path, filename, extension, size)
        VALUES (?, ?, ?, ?)
        """,
        samples_list
    )
    conn.commit()

