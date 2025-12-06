"""
CSV Embedding Script
Reads CSV files, generates embeddings using OpenAI API, and stores them in Supabase.
"""

import os
import csv
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize Supabase
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("PROJECT_URL and SUPABASE_API must be set in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_embedding(text: str, model: str = "text-embedding-3-small", max_retries: int = 3) -> List[float]:
    """
    Generate embedding for a text using OpenAI API with retry logic.
    
    Args:
        text: The text to embed
        model: The embedding model to use (text-embedding-3-small = 1536 dims, text-embedding-3-large = 3072 dims)
        max_retries: Maximum number of retry attempts
        
    Returns:
        List of floats representing the embedding
        
    Raises:
        Exception: If quota exceeded or other errors after retries
    """
    for attempt in range(max_retries):
        try:
            response = openai_client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            error_str = str(e)
            # Check if it's a quota or rate limit error
            if "429" in error_str or "quota" in error_str.lower() or "rate_limit" in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 60  # Wait 1, 2, 3 minutes
                    print(f"\n  ⚠ Rate limit exceeded. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded. Please wait and try again later.")
            else:
                # For other errors, raise immediately
                raise


def read_csv_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Read a CSV file and return rows as dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of dictionaries, one per row
    """
    rows = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(row)
        print(f"Read {len(rows)} rows from {file_path}")
        return rows
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {e}")
        raise


def check_existing_records(table_name: str, total_rows: int) -> int:
    """
    Check how many records already exist in the table to resume from the right point.
    
    Args:
        table_name: Supabase table name
        total_rows: Total number of rows in CSV
        
    Returns:
        Number of existing records
    """
    try:
        result = supabase.table(table_name).select("id", count="exact").execute()
        existing_count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
        if existing_count > 0:
            print(f"Found {existing_count} existing records in database. Will resume from row {existing_count + 1}.")
        return existing_count
    except Exception as e:
        print(f"Could not check existing records: {e}")
        return 0


def embed_and_store_csv(
    csv_file_path: str,
    table_name: str = "posts",
    batch_size: int = 50,  # Larger batches for faster processing
    title_column: str = None,
    body_column: str = None,
    start_from_row: int = 0  # Resume from a specific row
):
    """
    Read CSV file, generate embeddings, and store in Supabase.
    
    Args:
        csv_file_path: Path to the CSV file
        table_name: Supabase table name to store embeddings (default: "posts")
        batch_size: Number of rows to process in each batch
        title_column: Column name to use for title. If None, uses first column or "title"
        body_column: Column name to use for body/embedding. If None, combines all columns
    """
    print(f"\n{'='*60}")
    print(f"Processing CSV file: {csv_file_path}")
    print(f"{'='*60}\n")
    
    # Read CSV file
    rows = read_csv_file(csv_file_path)
    
    if not rows:
        print("No rows found in CSV file. Exiting.")
        return
    
    # Check for existing records and resume if needed
    if start_from_row == 0:
        start_from_row = check_existing_records(table_name, len(rows))
    
    if start_from_row > 0:
        print(f"Resuming from row {start_from_row + 1} (skipping first {start_from_row} rows)\n")
        rows = rows[start_from_row:]
    
    # Determine column names
    if not title_column:
        # Try to find a title column, or use first column
        possible_titles = ['title', 'Title', 'name', 'Name', 'subject', 'Subject']
        title_column = next((col for col in possible_titles if col in rows[0]), list(rows[0].keys())[0])
    
    if not body_column:
        # Try to find a body column, or combine all columns
        possible_bodies = ['body', 'Body', 'content', 'Content', 'text', 'Text', 'description', 'Description']
        body_column = next((col for col in possible_bodies if col in rows[0]), None)
    
    # Process rows in small batches to balance speed and progress preservation
    total_rows = len(rows)
    processed = 0
    
    for i in range(0, total_rows, batch_size):
        batch = rows[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_rows + batch_size - 1) // batch_size
        
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} rows)...")
        
        records_to_insert = []
        
        for idx, row in enumerate(batch):
            try:
                # Get title
                title = row.get(title_column, "") if title_column and title_column in row else ""
                
                # Get body text for embedding
                if body_column and body_column in row:
                    body_text = row[body_column]
                else:
                    # Combine all columns except title for body
                    body_parts = []
                    for key, value in row.items():
                        if key != title_column and value:
                            body_parts.append(f"{key}: {value}")
                    body_text = " | ".join(body_parts) if body_parts else title
                
                # Generate embedding from body text
                current_row = start_from_row + i + idx + 1
                print(f"  Row {current_row}/{start_from_row + total_rows}: Generating embedding...", end=" ")
                try:
                    embedding = get_embedding(body_text)
                    print("✓")
                except Exception as e:
                    if "quota" in str(e).lower() or "429" in str(e):
                        print(f"\n\n{'='*60}")
                        print("⚠ QUOTA EXCEEDED - Stopping script")
                        print(f"Processed {processed} rows successfully before hitting quota limit.")
                        print(f"To resume later, the script will automatically skip already processed rows.")
                        print(f"{'='*60}\n")
                        return
                    else:
                        raise
                
                # Prepare record for Supabase (matching the posts table schema)
                record = {
                    "title": title or "Untitled",
                    "body": body_text,
                    "embedding": embedding,
                }
                
                records_to_insert.append(record)
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"\n  ✗ Error processing row {i + idx + 1}: {e}")
                continue
        
        # Insert batch into Supabase (saves progress every 50 rows)
        if records_to_insert:
            max_retries = 3
            retry_count = 0
            insert_success = False
            
            while retry_count < max_retries and not insert_success:
                try:
                    result = supabase.table(table_name).insert(records_to_insert).execute()
                    
                    # Verify the insert was successful
                    if result.data and len(result.data) > 0:
                        processed += len(records_to_insert)
                        print(f"  ✓ Inserted {len(records_to_insert)} records into Supabase (IDs: {[r.get('id') for r in result.data[:3]]}...)\n")
                        insert_success = True
                    else:
                        print(f"  ⚠ Insert returned no data. Check Supabase permissions and table schema.\n")
                        print(f"  Attempted to insert: {len(records_to_insert)} records")
                        # Still count as processed to avoid infinite loops, but warn user
                        processed += len(records_to_insert)
                        insert_success = True
                        
                except Exception as e:
                    error_str = str(e).lower()
                    # Check if it's a transient network error (broken pipe, connection reset, etc.)
                    is_transient = any(keyword in error_str for keyword in ['broken pipe', 'connection', 'timeout', 'reset'])
                    
                    if is_transient and retry_count < max_retries - 1:
                        retry_count += 1
                        wait_time = retry_count * 2  # Wait 2, 4, 6 seconds
                        print(f"  ⚠ Transient error (attempt {retry_count}/{max_retries}): {e}")
                        print(f"  Retrying in {wait_time} seconds...\n")
                        time.sleep(wait_time)
                    else:
                        print(f"  ✗ Error inserting batch into Supabase: {e}\n")
                        if retry_count >= max_retries - 1:
                            print(f"  Failed after {max_retries} attempts. Skipping this batch.\n")
                        # Don't count failed inserts
                        break
        
        # Small delay between batches
        if i + batch_size < total_rows:
            time.sleep(0.2)
    
    print(f"\n{'='*60}")
    print(f"Completed! Processed {processed}/{total_rows} rows from {csv_file_path}")
    print(f"{'='*60}\n")


def main():
    """
    Main function to process CSV files.
    Update the CSV_FILE_PATHS list with your CSV file paths.
    """
    # CSV file paths (relative to backend directory)
    CSV_FILE_PATHS = [
        "../reddit_predictions/reddit_predictions_first_half.csv",
        "../reddit_predictions/reddit_predictions_second_half.csv",
    ]
    
    # Supabase table name (create this table in Supabase first)
    TABLE_NAME = "posts"
    
    # Optional: specify column names from your CSV
    # If None, script will try to auto-detect or use first column for title
    TITLE_COLUMN = None  # e.g., "title" or "name"
    BODY_COLUMN = None   # e.g., "body", "content", or "description"
    
    if not CSV_FILE_PATHS:
        print("Please update CSV_FILE_PATHS in the main() function with your CSV file paths.")
        return
    
    print("\n" + "="*60)
    print("CSV Embedding Script")
    print("="*60)
    print(f"OpenAI API Key: {'✓ Set' if OPENAI_API_KEY else '✗ Not Set'}")
    print(f"Supabase URL (PROJECT_URL): {'✓ Set' if SUPABASE_URL else '✗ Not Set'}")
    print(f"Supabase Key (SUPABASE_API): {'✓ Set' if SUPABASE_KEY else '✗ Not Set'}")
    print("="*60 + "\n")
    
    # Process each CSV file
    for csv_file in CSV_FILE_PATHS:
        if not os.path.exists(csv_file):
            print(f"Warning: CSV file not found: {csv_file}")
            continue
        
        try:
            embed_and_store_csv(
                csv_file_path=csv_file,
                table_name=TABLE_NAME,
                title_column=TITLE_COLUMN,
                body_column=BODY_COLUMN
            )
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            continue
    
    print("All CSV files processed!")


if __name__ == "__main__":
    main()

