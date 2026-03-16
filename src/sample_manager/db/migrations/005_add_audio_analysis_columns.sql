-- Migration: Add musical_key and duration to samples
ALTER TABLE samples ADD COLUMN musical_key TEXT;
ALTER TABLE samples ADD COLUMN duration REAL;
