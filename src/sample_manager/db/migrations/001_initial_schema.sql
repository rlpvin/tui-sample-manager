-- Samples table
CREATE TABLE samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    filename TEXT NOT NULL,
    extension TEXT,
    size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Many-to-many relationship
CREATE TABLE sample_tags (
    sample_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (sample_id, tag_id),
    FOREIGN KEY(sample_id) REFERENCES samples(id) ON DELETE CASCADE,
    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Ratings
CREATE TABLE ratings (
    sample_id INTEGER PRIMARY KEY,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    FOREIGN KEY(sample_id) REFERENCES samples(id) ON DELETE CASCADE
);

-- Collections
CREATE TABLE collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    rule TEXT
);

-- File hashes (duplicate detection)
CREATE TABLE file_hashes (
    sample_id INTEGER PRIMARY KEY,
    sha256 TEXT UNIQUE,
    FOREIGN KEY(sample_id) REFERENCES samples(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_samples_filename ON samples(filename);
CREATE INDEX idx_samples_extension ON samples(extension);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_hash_sha256 ON file_hashes(sha256);