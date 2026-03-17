import os
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from sample_manager.db.sample_repository import create_sample
from sample_manager.utils.batch import BatchProcessor


def test_db_rollback_on_error(test_db):
    """Verify that a database error triggers a rollback and doesn't partially commit."""
    # We patch get_connection in the repository module
    with patch("sample_manager.db.sample_repository.get_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Raise an error on execute
        mock_cursor.execute.side_effect = sqlite3.Error("Mock DB Error")

        with pytest.raises(sqlite3.Error):
            create_sample("path/to/fail", "fail.wav", ".wav", 100)

        # Verify rollback was called on the mock connection
        assert mock_conn.rollback.called


def test_batch_rename_missing_file(test_db, tmp_path):
    """Verify BatchProcessor handles missing source files gracefully."""
    # Register a file in DB that doesn't exist on disk
    from sample_manager.db.connection import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    missing_path = str(tmp_path / "missing.wav")
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("missing.wav", missing_path, ".wav"),
    )
    conn.commit()

    processor = BatchProcessor(log_callback=lambda x: None)
    count = processor.rename_samples([1], "missing", "new")

    assert count == 0
    # Entry should still exist in DB with old path
    cursor.execute("SELECT path FROM samples WHERE id=1")
    assert cursor.fetchone()["path"] == missing_path


def test_batch_rename_destination_exists(test_db, tmp_path):
    """Verify BatchProcessor doesn't overwrite existing files during rename."""
    f1 = tmp_path / "src.wav"
    f1.write_text("source")
    f2 = tmp_path / "dest.wav"
    f2.write_text("destination")

    from sample_manager.db.connection import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("src.wav", str(f1), ".wav"),
    )
    conn.commit()

    processor = BatchProcessor(log_callback=lambda x: None)
    # Try to rename src.wav to dest.wav
    count = processor.rename_samples([1], "src", "dest")

    assert count == 0
    assert f1.read_text() == "source"
    assert f2.read_text() == "destination"


def test_batch_normalize_temp_file_cleanup(test_db, tmp_path):
    """Verify temp files are cleaned up even on failure during normalization."""
    f1 = tmp_path / "norm.wav"
    f1.write_text("dummy audio")

    from sample_manager.db.connection import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO samples (filename, path, extension) VALUES (?, ?, ?)",
        ("norm.wav", str(f1), ".wav"),
    )
    conn.commit()

    processor = BatchProcessor(log_callback=lambda x: None)

    # Mock subprocess.run to fail
    with patch("subprocess.run", side_effect=Exception("FFmpeg failed")):
        count = processor.normalize_samples([1])
        assert count == 0

        # Check if temp file exists (it should be cleaned up)
        temp_path = str(f1) + ".tmp.wav"
        assert not os.path.exists(temp_path)
