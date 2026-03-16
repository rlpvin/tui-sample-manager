from sample_manager.db.rating_repository import set_rating


def test_set_rating(test_db):

    cursor = test_db.cursor()

    cursor.execute(
        "INSERT INTO samples (filename, path) VALUES (?, ?)",
        ("snare.wav", "/samples/snare.wav"),
    )

    sample_id = cursor.lastrowid
    test_db.commit()

    set_rating(sample_id, 5)

    cursor.execute("SELECT rating FROM ratings WHERE sample_id = ?", (sample_id,))

    rating = cursor.fetchone()[0]

    assert rating == 5
