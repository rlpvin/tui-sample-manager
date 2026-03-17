from sample_manager.db.sample_repository import create_sample
from sample_manager.db.tag_repository import (
    add_tag_to_sample,
    get_or_create_tag,
    get_tags_for_sample,
)


def test_tag_unique(test_db):

    cursor = test_db.cursor()

    get_or_create_tag(cursor, "drum")
    get_or_create_tag(cursor, "drum")

    cursor.execute("SELECT * FROM tags")

    rows = cursor.fetchall()

    assert len(rows) == 1


def test_add_tag_to_sample(test_db):

    create_sample(
        path="/samples/kick.wav",
        filename="kick.wav",
        extension="wav",
        size=1024,
    )

    cursor = test_db.cursor()

    get_or_create_tag(cursor, "drum")
    tag_name = "drum"
    sample_id = 1
    add_tag_to_sample(sample_id, tag_name)

    tags = get_tags_for_sample(sample_id)

    assert len(tags) == 1
    assert tags[0] == tag_name


def test_get_tags_for_sample(test_db):

    create_sample(
        path="/samples/kick.wav",
        filename="kick.wav",
        extension="wav",
        size=1024,
    )

    tag_name = "drum"
    sample_id = 1

    add_tag_to_sample(sample_id, tag_name)

    tags = get_tags_for_sample(sample_id)

    assert len(tags) == 1
    assert tags[0] == tag_name
