"""
Test script to verify we can insert data into Supabase without using Gemini API.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*60)
print("Testing Insert to Supabase (without Gemini)")
print("="*60)

# Create a dummy embedding vector (768 dimensions for Gemini embedding-001)
dummy_embedding = [0.1] * 768

print(f"\n1. Created dummy embedding vector (dimension: {len(dummy_embedding)})")

# Test insert
print("\n2. Inserting test record to Supabase...")
try:
    test_record = {
        "title": "Test Post - No API Key Needed",
        "body": "This is a test to verify Supabase inserts work",
        "embedding": dummy_embedding
    }
    
    print(f"   Attempting to insert: {test_record['title']}")
    result = supabase.table("posts").insert(test_record).execute()
    
    print(f"   Result type: {type(result)}")
    print(f"   Has data attribute: {hasattr(result, 'data')}")
    
    if hasattr(result, 'data'):
        if result.data:
            print(f"   ✓ Successfully inserted record!")
            print(f"   Record ID: {result.data[0].get('id')}")
            print(f"   Full result: {result.data[0]}")
            
            # Verify it's there
            print("\n3. Verifying record exists...")
            verify = supabase.table("posts").select("id, title, body").eq("id", result.data[0].get('id')).execute()
            if verify.data:
                print(f"   ✓ Record verified! Found: {verify.data[0]}")
                
                # Count all records
                count_result = supabase.table("posts").select("id", count="exact").execute()
                total = count_result.count if hasattr(count_result, 'count') else len(count_result.data) if count_result.data else 0
                print(f"\n   Total records in table now: {total}")
            else:
                print("   ⚠ Record not found in verification query")
        else:
            print("   ⚠ Insert returned no data in result.data")
            print(f"   Result object: {result}")
    else:
        print(f"   ⚠ Result doesn't have 'data' attribute")
        print(f"   Result: {result}")
        
except Exception as e:
    print(f"   ❌ Error inserting: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

