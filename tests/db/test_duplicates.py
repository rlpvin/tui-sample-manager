import os
import pytest
from sample_manager.db.sample_repository import create_sample, get_duplicates_grouped
from sample_manager.utils.hashing import calculate_hash

def test_calculate_hash(tmp_path):
    file1 = tmp_path / "test1.wav"
    file1.write_bytes(b"content1")
    file2 = tmp_path / "test2.wav"
    file2.write_bytes(b"content1")
    file3 = tmp_path / "test3.wav"
    file3.write_bytes(b"content2")
    
    hash1 = calculate_hash(str(file1))
    hash2 = calculate_hash(str(file2))
    hash3 = calculate_hash(str(file3))
    
    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64 # SHA-256 length

def test_get_duplicates_grouped(test_db):
    # Clear existing samples if any
    cursor = test_db.cursor()
    cursor.execute("DELETE FROM samples")
    test_db.commit()
    
    h1 = "hash_alpha"
    h2 = "hash_beta"
    
    # Group 1 (3 samples)
    create_sample("/p1.wav", "p1.wav", ".wav", 100, h1)
    create_sample("/p2.wav", "p2.wav", ".wav", 100, h1)
    create_sample("/p3.wav", "p3.wav", ".wav", 100, h1)
    
    # Group 2 (2 samples)
    create_sample("/p4.wav", "p4.wav", ".wav", 200, h2)
    create_sample("/p5.wav", "p5.wav", ".wav", 200, h2)
    
    # Single sample (no duplicate)
    create_sample("/p6.wav", "p6.wav", ".wav", 300, "unique_hash")
    
    groups = get_duplicates_grouped()
    
    assert len(groups) == 2
    
    # Find h1 group
    g1 = next(g for g in groups if g["hash"] == h1)
    assert len(g1["samples"]) == 3
    
    # Find h2 group
    g2 = next(g for g in groups if g["hash"] == h2)
    assert len(g2["samples"]) == 2
