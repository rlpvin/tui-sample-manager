from sample_manager.db.sample_repository import search_samples, create_sample
from sample_manager.db.connection import get_connection

def test_search_samples_basic(test_db):
    create_sample("/samples/kick.wav", "kick.wav", ".wav", 2048)
    
    # New signature uses filters dict
    results = search_samples({"query": "kick"})
    assert len(results) == 1
    assert results[0]["filename"] == "kick.wav"

def test_search_samples_tag_filter(test_db):
    # Add sample and tag
    create_sample("/samples/drum.wav", "drum.wav", ".wav", 1024)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tags (name) VALUES (?)", ("percussion",))
    tag_id = cursor.lastrowid
    cursor.execute("SELECT id FROM samples WHERE filename='drum.wav'")
    sample_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO sample_tags (sample_id, tag_id) VALUES (?, ?)", (sample_id, tag_id))
    conn.commit()

    results = search_samples({"tag": "percussion"})
    assert len(results) == 1
    assert results[0]["filename"] == "drum.wav"

def test_search_samples_rating_filter(test_db):
    create_sample("/samples/good.wav", "good.wav", ".wav", 1024)
    create_sample("/samples/bad.wav", "bad.wav", ".wav", 1024)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM samples WHERE filename='good.wav'")
    id_good = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM samples WHERE filename='bad.wav'")
    id_bad = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO ratings (sample_id, rating) VALUES (?, ?)", (id_good, 5))
    cursor.execute("INSERT INTO ratings (sample_id, rating) VALUES (?, ?)", (id_bad, 2))
    conn.commit()

    results = search_samples({"rating": (">", 3)})
    assert len(results) == 1
    assert results[0]["filename"] == "good.wav"

def test_search_samples_sorting(test_db):
    create_sample("/samples/b.wav", "b.wav", ".wav", 1024)
    create_sample("/samples/a.wav", "a.wav", ".wav", 1024)
    
    results = search_samples(sort_by="filename", sort_order="ASC")
    assert results[0]["filename"] == "a.wav"
    assert results[1]["filename"] == "b.wav"
    
    results = search_samples(sort_by="filename", sort_order="DESC")
    assert results[0]["filename"] == "b.wav"
    assert results[1]["filename"] == "a.wav"

def test_search_samples_rating_sorting(test_db):
    create_sample("/samples/r1.wav", "r1.wav", ".wav", 1024)
    create_sample("/samples/r2.wav", "r2.wav", ".wav", 1024)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM samples WHERE filename='r1.wav'")
    id1 = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM samples WHERE filename='r2.wav'")
    id2 = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO ratings (sample_id, rating) VALUES (?, ?)", (id1, 1))
    cursor.execute("INSERT INTO ratings (sample_id, rating) VALUES (?, ?)", (id2, 5))
    conn.commit()
    
    # Sort by rating ASC (1 then 5)
    results = search_samples(sort_by="rating", sort_order="ASC")
    assert results[0]["filename"] == "r1.wav"
    assert results[1]["filename"] == "r2.wav"
    
    # Sort by rating DESC (5 then 1)
    results = search_samples(sort_by="rating", sort_order="DESC")
    assert results[0]["filename"] == "r2.wav"
    assert results[1]["filename"] == "r1.wav"
