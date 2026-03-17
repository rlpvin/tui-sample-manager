from sample_manager.app.parser import Command
from sample_manager.app.router import CommandRouter
from sample_manager.db.tag_repository import (
    add_tag_to_sample,
    get_all_tags,
    remove_tag_from_sample,
)


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


def test_remove_tag_from_sample(test_db):
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO samples (filename, path) VALUES (?, ?)",
        ("snare.wav", "/samples/snare.wav"),
    )
    sample_id = cursor.lastrowid
    test_db.commit()

    add_tag_to_sample(sample_id, "snare")
    remove_tag_from_sample(sample_id, "snare")

    cursor.execute("SELECT COUNT(*) FROM sample_tags WHERE sample_id = ?", (sample_id,))
    count = cursor.fetchone()[0]
    assert count == 0


def test_get_all_tags(test_db):
    add_tag_to_sample(1, "abc")
    add_tag_to_sample(1, "xyz")

    tags = get_all_tags()
    assert "abc" in tags
    assert "xyz" in tags
    assert len(tags) >= 2


def test_bulk_tag(test_db):
    cursor = test_db.cursor()
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("kick1.wav", "/s/k1.wav", "wav"),
    )
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("kick2.wav", "/s/k2.wav", "wav"),
    )
    test_db.commit()

    router = CommandRouter()
    # bulk-tag <query> <tag>
    result = router.bulk_tag(["kick", "electronic"])

    assert "Added tag 'electronic' to 2 samples" in result

    tags1 = router.route(Command("tags", []))
    assert "electronic" in tags1
