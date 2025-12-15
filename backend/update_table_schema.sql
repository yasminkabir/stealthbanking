-- Update the posts table to use 1536 dimensions for OpenAI embeddings
-- Run this in your Supabase SQL Editor

-- Option 1: Drop and recreate (if you don't mind losing existing data)
DROP TABLE IF EXISTS posts CASCADE;

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  embedding vector(1536)
);

-- Option 2: If you want to keep existing data, you'll need to:
-- 1. Create a new table with correct dimensions
-- 2. Migrate data (if any)
-- 3. Drop old table and rename new one
-- This is more complex, so Option 1 is recommended if the table is empty or you can recreate

