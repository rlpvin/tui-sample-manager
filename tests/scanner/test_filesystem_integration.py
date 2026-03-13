import os
from pathlib import Path

import pytest

from sample_manager.scanner.directories import register_directory, get_registered_directories
from sample_manager.scanner.file_scanner import scan_directory, is_supported_audio_file
from sample_manager.scanner.metadata import extract_metadata
from sample_manager.scanner.indexer import index_samples, remove_deleted_files
from sample_manager.db.sample_repository import get_all_samples

@pytest.fixture
def sample_library(tmp_path):

    root = tmp_path / "samples"
    root.mkdir()

    kicks = root / "kicks"
    kicks.mkdir()

    snares = root / "snares"
    snares.mkdir()

    # create supported files
    (kicks / "kick1.wav").write_bytes(b"audio")
    (kicks / "kick2.aif").write_bytes(b"audio")
    (snares / "snare1.flac").write_bytes(b"audio")

    # unsupported file
    (root / "readme.txt").write_text("ignore")

    return root

def test_register_directory(sample_library):

    register_directory(str(sample_library))

    directories = get_registered_directories()

    assert str(sample_library) in directories

def test_supported_audio_formats():

    assert is_supported_audio_file(Path("kick.wav"))
    assert is_supported_audio_file(Path("snare.mp3"))
    assert is_supported_audio_file(Path("loop.flac"))
    assert is_supported_audio_file(Path("pad.aif"))

    assert not is_supported_audio_file(Path("notes.txt"))

def test_recursive_scan(sample_library):

    results = list(scan_directory(str(sample_library)))

    names = {p.name for p in results}

    assert "kick1.wav" in names
    assert "kick2.aif" in names
    assert "snare1.flac" in names

    # ensure unsupported file ignored
    assert "readme.txt" not in names

def test_metadata_extraction(sample_library):

    file_path = sample_library / "kicks" / "kick1.wav"

    meta = extract_metadata(file_path)

    assert meta["filename"] == "kick1.wav"
    assert meta["extension"] == "wav"
    assert meta["size"] > 0
    assert meta["path"] == str(file_path)

def test_index_samples(sample_library):

    register_directory(str(sample_library))

    index_samples()

    samples = get_all_samples()

    filenames = {s["filename"] for s in samples}

    assert "kick1.wav" in filenames
    assert "kick2.aif" in filenames
    assert "snare1.flac" in filenames

def test_remove_deleted_files(sample_library):

    register_directory(str(sample_library))

    index_samples()

    samples = get_all_samples()

    assert len(samples) > 0

    # delete a file
    file_to_delete = sample_library / "kicks" / "kick1.wav"
    os.remove(file_to_delete)

    remove_deleted_files()

    samples_after = get_all_samples()

    paths = {s["path"] for s in samples_after}

    assert str(file_to_delete) not in paths
