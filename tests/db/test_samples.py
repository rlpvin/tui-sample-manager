from sample_manager.db.sample_repository import (
    create_sample,
    delete_sample,
)


def test_create_sample(test_db):

    create_sample(
        path="/samples/kick.wav",
        filename="kick.wav",
        extension="wav",
        size=1024,
    )

    cursor = test_db.cursor()

    cursor.execute("SELECT * FROM samples")

    row = cursor.fetchone()

    assert row["filename"] == "kick.wav"


def test_delete_sample(test_db):

    create_sample(
        path="/samples/snare.wav",
        filename="snare.wav",
        extension="wav",
        size=2000,
    )

    cursor = test_db.cursor()
    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    delete_sample(sample_id)

    cursor.execute("SELECT * FROM samples")

    assert cursor.fetchone() is None
