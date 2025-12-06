"""
Test script to verify we can insert data into Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API")
SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("❌ GEMINI_API not set")
    exit(1)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*60)
print("Testing Insert to Supabase")
print("="*60)

# Generate a test embedding
print("\n1. Generating test embedding...")
try:
    test_text = "This is a test post for embedding"
    result = genai.embed_content(
        model="models/embedding-001",
        content=test_text,
        task_type="retrieval_document"
    )
    embedding = result['embedding']
    print(f"   ✓ Embedding generated (dimension: {len(embedding)})")
except Exception as e:
    print(f"   ❌ Error generating embedding: {e}")
    exit(1)

# Test insert
print("\n2. Inserting test record to Supabase...")
try:
    test_record = {
        "title": "Test Post",
        "body": test_text,
        "embedding": embedding
    }
    
    result = supabase.table("posts").insert(test_record).execute()
    
    if result.data:
        print(f"   ✓ Successfully inserted record!")
        print(f"   Record ID: {result.data[0].get('id')}")
        
        # Verify it's there
        print("\n3. Verifying record exists...")
        verify = supabase.table("posts").select("id, title").eq("id", result.data[0].get('id')).execute()
        if verify.data:
            print(f"   ✓ Record verified! Found: {verify.data[0]}")
        else:
            print("   ⚠ Record not found in verification query")
    else:
        print("   ⚠ Insert returned no data")
        
except Exception as e:
    print(f"   ❌ Error inserting: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

