from sample_manager.db.connection import get_connection


def create_tag(name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO tags (name) VALUES (?)",
        (name,),
    )

    conn.commit()


def get_all_tags():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tags")
    return cursor.fetchall()


def delete_tag(tag_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tags WHERE id=?", (tag_id,))
    conn.commit()
