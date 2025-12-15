-- Create a function in Supabase for vector similarity search
-- Run this in your Supabase SQL Editor

CREATE OR REPLACE FUNCTION match_posts(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id bigint,
  title text,
  body text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    posts.id,
    posts.title,
    posts.body,
    1 - (posts.embedding <=> query_embedding) as similarity
  FROM posts
  WHERE 1 - (posts.embedding <=> query_embedding) > match_threshold
  ORDER BY posts.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Note: The <=> operator is the cosine distance operator in pgvector
-- We convert it to similarity by doing 1 - distance


