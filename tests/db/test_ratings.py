import pytest

from sample_manager.db.rating_repository import remove_rating, set_rating
from sample_manager.db.sample_repository import create_sample


def test_rating_valid(test_db):

    cursor = test_db.cursor()

    create_sample("/test.wav", "test.wav", "wav", 100)

    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    set_rating(sample_id, 5)

    cursor.execute("SELECT rating FROM ratings")

    assert cursor.fetchone()["rating"] == 5


def test_rating_invalid(test_db):

    cursor = test_db.cursor()

    create_sample("/test.wav", "test.wav", "wav", 100)

    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    with pytest.raises(ValueError):
        set_rating(sample_id, 7)


def test_rating_removal(test_db):
    cursor = test_db.cursor()
    create_sample("/remove.wav", "remove.wav", "wav", 100)
    cursor.execute("SELECT id FROM samples WHERE filename='remove.wav'")
    sample_id = cursor.fetchone()["id"]

    set_rating(sample_id, 3)
    remove_rating(sample_id)

    cursor.execute("SELECT COUNT(*) FROM ratings WHERE sample_id = ?", (sample_id,))
    assert cursor.fetchone()[0] == 0
