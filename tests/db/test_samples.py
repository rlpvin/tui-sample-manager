from sample_manager.db.sample_repository import (
    bulk_create_samples,
    create_sample,
    delete_sample,
    get_all_samples,
    get_sample_by_id,
    get_sample_count,
    search_samples,
)


def create_test_sample():
    create_sample(
        path="/samples/kick.wav",
        filename="kick.wav",
        extension="wav",
        size=1024,
    )


def test_create_sample(test_db):

    cursor = test_db.cursor()

    create_test_sample()

    cursor.execute("SELECT * FROM samples")

    row = cursor.fetchone()

    assert row["filename"] == "kick.wav"


def test_delete_sample(test_db):

    cursor = test_db.cursor()

    create_test_sample()

    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    delete_sample(sample_id)

    cursor.execute("SELECT * FROM samples")

    assert cursor.fetchone() is None


def test_get_sample_by_id(test_db):

    cursor = test_db.cursor()

    create_test_sample()

    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    sample = get_sample_by_id(sample_id)

    assert sample["filename"] == "kick.wav"


def test_get_all_samples(test_db):

    create_test_sample()

    samples = get_all_samples()

    assert len(samples) == 1
    assert samples[0]["filename"] == "kick.wav"


def test_bulk_create_samples(test_db):

    samples_data = [
        {
            "path": "/samples/snare.wav",
            "filename": "snare.wav",
            "extension": "wav",
            "size": 2048,
        },
        {
            "path": "/samples/hihat.wav",
            "filename": "hihat.wav",
            "extension": "wav",
            "size": 512,
        },
    ]

    bulk_create_samples(samples_data)

    samples = get_all_samples()

    assert len(samples) == 2
    assert samples[0]["filename"] == "hihat.wav"
    assert samples[1]["filename"] == "snare.wav"


def test_search_samples(test_db):

    create_test_sample()

    results = search_samples("kick")

    assert len(results) == 1
    assert results[0]["filename"] == "kick.wav"


def test_get_sample_count(test_db):

    create_test_sample()

    count = get_sample_count()

    assert count == 1
