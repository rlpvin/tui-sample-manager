from sample_manager.db.tag_repository import add_tag_to_sample


def test_add_tag_to_sample(test_db):

    cursor = test_db.cursor()

    cursor.execute(
        "INSERT INTO samples (filename, path) VALUES (?, ?)",
        ("kick.wav", "/samples/kick.wav"),
    )

    sample_id = cursor.lastrowid
    test_db.commit()

    add_tag_to_sample(sample_id, "drum")

    cursor.execute(
        """
        SELECT t.name
        FROM tags t
        JOIN sample_tags st ON t.id = st.tag_id
        WHERE st.sample_id = ?
    """,
        (sample_id,),
    )

    tags = cursor.fetchall()

    assert tags[0][0] == "drum"
