-- Add hash column to samples table
ALTER TABLE samples ADD COLUMN hash TEXT;

-- Create index for fast duplicate lookup
CREATE INDEX idx_samples_hash ON samples(hash);
