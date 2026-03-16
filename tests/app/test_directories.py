from sample_manager.scanner.directories import (
    register_directory,
    remove_directory,
)


def test_register_directory(test_db, tmp_path):
    cursor = test_db.cursor()

    fake_dir = tmp_path / "samples"
    fake_dir.mkdir()

    resolved_path = str(fake_dir.resolve())
    register_directory(resolved_path)

    cursor.execute("SELECT path FROM sample_directories")

    result = cursor.fetchone()

    assert result[0] == resolved_path


def test_remove_directory(test_db, tmp_path):

    fake_dir = tmp_path / "samples"
    fake_dir.mkdir()

    resolved_path = str(fake_dir.resolve())

    register_directory(resolved_path)
    remove_directory(resolved_path)

    cursor = test_db.cursor()

    cursor.execute("SELECT * FROM sample_directories")

    result = cursor.fetchall()

    assert result == []
