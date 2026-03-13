from sample_manager.db.tag_repository import create_tag


def test_tag_unique(test_db):

    create_tag("drum")
    create_tag("drum")

    cursor = test_db.cursor()

    cursor.execute("SELECT * FROM tags")

    rows = cursor.fetchall()

    assert len(rows) == 1
