from sample_manager.db.sample_repository import create_sample
from sample_manager.db.tag_repository import get_or_create_tag


def test_sample_tag_relationship(test_db):

    cursor = test_db.cursor()

    create_sample("/samples/kick.wav", "kick.wav", "wav", 1000)

    cursor.execute("SELECT id FROM samples")
    sample_id = cursor.fetchone()["id"]

    get_or_create_tag(cursor, "drum")

    cursor.execute("SELECT id FROM tags")
    tag_id = cursor.fetchone()["id"]

    cursor.execute(
        "INSERT INTO sample_tags (sample_id, tag_id) VALUES (?, ?)",
        (sample_id, tag_id),
    )

    test_db.commit()

    cursor.execute(
        """
        SELECT tags.name
        FROM tags
        JOIN sample_tags ON tags.id = sample_tags.tag_id
        WHERE sample_tags.sample_id = ?
        """,
        (sample_id,),
    )

    tag = cursor.fetchone()

    assert tag["name"] == "drum"
