import pytest

from sample_manager.db.rating_repository import set_rating
from sample_manager.db.sample_repository import create_sample


def test_rating_valid(test_db):

    create_sample("/test.wav", "test.wav", "wav", 100)

    cursor = test_db.cursor()
    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    set_rating(sample_id, 5)

    cursor.execute("SELECT rating FROM ratings")

    assert cursor.fetchone()["rating"] == 5


def test_rating_invalid(test_db):

    create_sample("/test.wav", "test.wav", "wav", 100)

    cursor = test_db.cursor()
    cursor.execute("SELECT id FROM samples")

    sample_id = cursor.fetchone()["id"]

    with pytest.raises(Exception):
        set_rating(sample_id, 7)
