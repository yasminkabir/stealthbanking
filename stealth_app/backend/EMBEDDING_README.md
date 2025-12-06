# CSV Embedding Script

This script reads CSV files, generates embeddings using Google's Gemini API, and stores them in Supabase.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `backend` directory with:
   ```
   GEMINI_API=your_gemini_api_key_here
   PROJECT_URL=your_supabase_url_here
   SUPABASE_API=your_supabase_key_here
   ```

3. **Enable pgvector extension in Supabase:**
   In your Supabase SQL editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

4. **Create Supabase table:**
   In your Supabase dashboard, create a table called `posts` with the following schema:
   ```sql
   CREATE TABLE posts (
     id SERIAL PRIMARY KEY,
     title TEXT NOT NULL,
     body TEXT NOT NULL,
     embedding vector(768)
   );
   ```
   
   Note: Gemini's `embedding-001` model produces 768-dimensional vectors. If you're using a different model, adjust the vector dimension accordingly.

## Usage

1. **Update the script:**
   Open `embed_csv.py` and update the `CSV_FILE_PATHS` list in the `main()` function with your CSV file paths:
   ```python
   CSV_FILE_PATHS = [
       "path/to/your/file1.csv",
       "path/to/your/file2.csv",
   ]
   ```

2. **Optional configuration:**
   - `TABLE_NAME`: Change the Supabase table name (default: "posts")
   - `TITLE_COLUMN`: Specify which CSV column to use for the title. If `None`, script will auto-detect.
   - `BODY_COLUMN`: Specify which CSV column to use for the body/embedding. If `None`, all columns will be combined.

3. **Run the script:**
   ```bash
   python embed_csv.py
   ```

## How it works

- Reads each CSV file row by row
- For each row:
  - Extracts a title (from specified column or auto-detected)
  - Creates body text (from specified column or by combining all columns)
  - Generates an embedding using Gemini's `embedding-001` model (768 dimensions)
  - Stores title, body, and embedding in Supabase `posts` table
- Processes rows in batches to avoid rate limiting

## Querying with Vector Search

Once your embeddings are stored, you can perform similarity searches:

```sql
-- Find similar posts using cosine distance
SELECT * FROM posts 
ORDER BY embedding <-> '[your_query_embedding]' 
LIMIT 5;
```

Or with filtering:

```sql
-- Find similar posts with filtering
SELECT * FROM posts 
WHERE title ILIKE '%keyword%'
ORDER BY embedding <-> '[your_query_embedding]' 
LIMIT 5;
```

## Notes

- The script includes rate limiting delays to avoid API limits
- Progress is displayed for each batch
- Errors for individual rows are caught and logged without stopping the entire process

