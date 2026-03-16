from sample_manager.db.sample_repository import get_sample_count


def test_sample_count(test_db):

    cursor = test_db.cursor()

    cursor.execute(
        "INSERT INTO samples (filename, path) VALUES (?, ?)",
        ("kick.wav", "/samples/kick.wav"),
    )

    cursor.execute(
        "INSERT INTO samples (filename, path) VALUES (?, ?)",
        ("snare.wav", "/samples/snare.wav"),
    )

    test_db.commit()

    count = get_sample_count()

    assert count == 2
