from sample_manager.db.connection import get_connection


def set_rating(sample_id, rating):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO ratings (sample_id, rating)
        VALUES (?, ?)
        ON CONFLICT(sample_id)
        DO UPDATE SET rating=excluded.rating
        """,
        (sample_id, rating),
    )

    conn.commit()


def get_rating(sample_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT rating FROM ratings WHERE sample_id=?",
        (sample_id,),
    )

    row = cursor.fetchone()

    return row["rating"] if row else None
