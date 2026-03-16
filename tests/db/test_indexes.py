from sample_manager.db.connection import get_connection


def test_indexes_exist():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")

    indexes = {row[0] for row in cursor.fetchall()}

    assert "idx_samples_filename" in indexes
    assert "idx_samples_extension" in indexes
    assert "idx_tags_name" in indexes
    assert "idx_hash_sha256" in indexes
