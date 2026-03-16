from sample_manager.db.sample_repository import search_samples


def test_search_samples(test_db):

    cursor = test_db.cursor()

    cursor.execute(
        "INSERT INTO samples (filename, path) VALUES (?, ?)",
        ("kick.wav", "/samples/kick.wav"),
    )

    test_db.commit()

    results = search_samples("kick")

    assert len(results) == 1
    assert results[0][1] == "kick.wav"
