from sample_manager.db.connection import get_connection
from sample_manager.db.sample_repository import bulk_create_samples
from sample_manager.scanner.directories import get_registered_directories
from sample_manager.scanner.file_scanner import scan_directory
from sample_manager.scanner.metadata import extract_metadata
from sample_manager.utils.hashing import calculate_hash


def index_samples():
    directories = get_registered_directories()
    all_metadata = []

    for directory in directories:
        print(f"Scanning: {directory}")
        for path in scan_directory(directory):
            meta = extract_metadata(path)
            # Store as a tuple for the DB
            all_metadata.append({
                "path": meta["path"],
                "filename": meta["filename"],
                "extension": meta["extension"],
                "size": meta["size"],
                "hash": calculate_hash(path)
            })

    if all_metadata:
        bulk_create_samples(all_metadata)
        print(f"Successfully indexed {len(all_metadata)} samples.")

def remove_deleted_files():
    """
    Remove database entries for files that no longer exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, path FROM samples")

    rows = cursor.fetchall()

    for row in rows:

        import os

        if not os.path.exists(row["path"]):

            cursor.execute(
                "DELETE FROM samples WHERE id=?",
                (row["id"],),
            )

    conn.commit()


def reindex():
    """
    Full reindex operation.
    """

    remove_deleted_files()
    index_samples()