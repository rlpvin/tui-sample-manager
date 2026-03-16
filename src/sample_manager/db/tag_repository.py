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


def remove_tag_from_sample(sample_id: int, tag_name: str):
    """
    Remove a tag from a sample.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM sample_tags 
        WHERE sample_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)
        """,
        (sample_id, tag_name),
    )

    conn.commit()


def get_all_tags():
    """
    Get a list of all existing tags.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM tags ORDER BY name ASC")
    rows = cursor.fetchall()

    return [row[0] for row in rows]
