"""
Test script to verify OpenAI embeddings and Supabase inserts with 1536 dimensions.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import openai

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

print("="*60)
print("OpenAI + Supabase Connection Test")
print("="*60)
print(f"OPENAI_API_KEY: {'✓ Set' if OPENAI_API_KEY else '✗ Not Set'}")
print(f"PROJECT_URL: {'✓ Set' if SUPABASE_URL else '✗ Not Set'}")
print(f"SUPABASE_API: {'✓ Set' if SUPABASE_KEY else '✗ Not Set'}")

if not OPENAI_API_KEY:
    print("\n❌ ERROR: OPENAI_API_KEY not found in .env file")
    exit(1)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ ERROR: Missing Supabase credentials in .env file")
    exit(1)

# Initialize OpenAI
try:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    print("\n✓ OpenAI client created successfully")
except Exception as e:
    print(f"\n❌ ERROR creating OpenAI client: {e}")
    exit(1)

# Initialize Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Supabase client created successfully")
except Exception as e:
    print(f"\n❌ ERROR creating Supabase client: {e}")
    exit(1)

# Generate test embedding
print("\n" + "="*60)
print("Step 1: Generating OpenAI Embedding")
print("="*60)

try:
    test_text = "This is a test post to verify OpenAI embeddings work with Supabase"
    print(f"Text: {test_text}")
    print("Generating embedding...")
    
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=test_text
    )
    
    embedding = response.data[0].embedding
    dimension = len(embedding)
    
    print(f"✓ Embedding generated successfully!")
    print(f"  Dimension: {dimension}")
    print(f"  First 5 values: {embedding[:5]}")
    
    if dimension != 1536:
        print(f"\n⚠ WARNING: Expected 1536 dimensions, got {dimension}")
        print("  Your Supabase table should use vector({dimension})")
    else:
        print("  ✓ Dimension matches expected 1536 for OpenAI text-embedding-3-small")
        
except Exception as e:
    print(f"\n❌ ERROR generating embedding: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test insert to Supabase
print("\n" + "="*60)
print("Step 2: Inserting to Supabase")
print("="*60)

try:
    test_record = {
        "title": "Test Post - OpenAI Embedding",
        "body": test_text,
        "embedding": embedding
    }
    
    print(f"Attempting to insert record...")
    print(f"  Title: {test_record['title']}")
    print(f"  Embedding dimension: {len(embedding)}")
    
    result = supabase.table("posts").insert(test_record).execute()
    
    if result.data and len(result.data) > 0:
        record_id = result.data[0].get('id')
        print(f"\n✓ Successfully inserted record!")
        print(f"  Record ID: {record_id}")
        
        # Verify it's there
        print("\n" + "="*60)
        print("Step 3: Verifying Record")
        print("="*60)
        
        verify = supabase.table("posts").select("id, title, body").eq("id", record_id).execute()
        if verify.data:
            print(f"✓ Record verified in database!")
            print(f"  {verify.data[0]}")
            
            # Count all records
            count_result = supabase.table("posts").select("id", count="exact").execute()
            total = count_result.count if hasattr(count_result, 'count') else len(count_result.data) if count_result.data else 0
            print(f"\n  Total records in table: {total}")
            
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED!")
            print("="*60)
            print("You're ready to run the full embedding script!")
        else:
            print("⚠ Record not found in verification query")
    else:
        print("⚠ Insert returned no data")
        print(f"  Result: {result}")
        
except Exception as e:
    print(f"\n❌ ERROR inserting to Supabase: {e}")
    error_str = str(e)
    
    if "expected" in error_str and "dimensions" in error_str:
        print("\n⚠ DIMENSION MISMATCH ERROR")
        print("Your Supabase table has the wrong vector dimension.")
        print(f"OpenAI embeddings are {dimension} dimensions.")
        print("\nRun this SQL in Supabase to fix it:")
        print("""
DROP TABLE IF EXISTS posts CASCADE;

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  embedding vector(1536)
);
        """)
    else:
        import traceback
        traceback.print_exc()

print("\n" + "="*60)

