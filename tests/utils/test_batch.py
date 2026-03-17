import os

from sample_manager.db.sample_repository import get_sample_by_id
from sample_manager.utils.batch import BatchProcessor


def test_rename_samples(test_db, tmp_path):
    # Setup mock files
    f1 = tmp_path / "kick_01.wav"
    f1.write_text("dummy")
    f2 = tmp_path / "snare_01.wav"
    f2.write_text("dummy")

    # Insert samples into mock DB (or assume mock_db fixture handles it)
    from sample_manager.db.connection import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("kick_01.wav", str(f1), ".wav"),
    )
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("snare_01.wav", str(f2), ".wav"),
    )
    conn.commit()

    processor = BatchProcessor()
    # Rename '01' to '02'
    count = processor.rename_samples([1, 2], "01", "02")

    assert count == 2
    assert os.path.exists(tmp_path / "kick_02.wav")
    assert not os.path.exists(f1)

    # Verify DB update
    s = get_sample_by_id(1)
    assert s["filename"] == "kick_02.wav"
    assert s["path"] == str(tmp_path / "kick_02.wav")


def test_tag_samples(test_db):
    from sample_manager.db.tag_repository import add_tag_to_sample, get_tags_for_sample

    # Filtered IDs
    ids = [1, 2]
    tag_name = "batch_test"

    for sid in ids:
        add_tag_to_sample(sid, tag_name)

    tags1 = get_tags_for_sample(1)
    tags2 = get_tags_for_sample(2)

    assert tag_name in tags1
    assert tag_name in tags2
