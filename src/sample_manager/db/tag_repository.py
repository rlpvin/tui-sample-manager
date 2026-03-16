from sample_manager.db.connection import get_connection


def get_or_create_tag(cursor, tag_name: str):
    cursor.execute(
        "SELECT id FROM tags WHERE name = ?",
        (tag_name,),
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO tags (name) VALUES (?)",
        (tag_name,),
    )

    return cursor.lastrowid


def add_tag_to_sample(sample_id: int, tag_name: str):
    """
    Attach a tag to a sample.
    """

    conn = get_connection()
    cursor = conn.cursor()

    tag_id = get_or_create_tag(cursor, tag_name)

    cursor.execute(
        """
        INSERT OR IGNORE INTO sample_tags (sample_id, tag_id)
        VALUES (?, ?)
        """,
        (sample_id, tag_id),
    )

    conn.commit()


def get_tags_for_sample(sample_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT t.name
        FROM tags t
        JOIN sample_tags st ON t.id = st.tag_id
        WHERE st.sample_id = ?
        """,
        (sample_id,),
    )

    rows = cursor.fetchall()

    return [row[0] for row in rows]
