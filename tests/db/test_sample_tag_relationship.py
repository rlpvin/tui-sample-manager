from sample_manager.db.sample_repository import create_sample
from sample_manager.db.tag_repository import create_tag


def test_sample_tag_relationship(test_db):
    """
    Verify that samples and tags can be linked through sample_tags.
    """

    cursor = test_db.cursor()

    # Create sample
    create_sample("/samples/kick.wav", "kick.wav", "wav", 1000)

    cursor.execute("SELECT id FROM samples")
    sample_id = cursor.fetchone()["id"]

    # Create tag
    create_tag("drum")

    cursor.execute("SELECT id FROM tags")
    tag_id = cursor.fetchone()["id"]

    # Link them
    cursor.execute(
        "INSERT INTO sample_tags (sample_id, tag_id) VALUES (?, ?)",
        (sample_id, tag_id),
    )

    test_db.commit()

    # Verify relationship
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