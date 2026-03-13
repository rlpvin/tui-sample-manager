def test_tables_exist(test_db):

    cursor = test_db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

    tables = {row[0] for row in cursor.fetchall()}

    assert "samples" in tables
    assert "tags" in tables
    assert "sample_tags" in tables
    assert "ratings" in tables
    assert "collections" in tables
    assert "file_hashes" in tables
