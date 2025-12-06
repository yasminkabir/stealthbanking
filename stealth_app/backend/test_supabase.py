"""
Test script to verify Supabase connection and check for existing records.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

print("="*60)
print("Supabase Connection Test")
print("="*60)
print(f"PROJECT_URL: {'✓ Set' if SUPABASE_URL else '✗ Not Set'}")
print(f"SUPABASE_API: {'✓ Set' if SUPABASE_KEY else '✗ Not Set'}")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("\n❌ ERROR: Missing Supabase credentials in .env file")
    exit(1)

# Initialize Supabase
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("\n✓ Supabase client created successfully")
except Exception as e:
    print(f"\n❌ ERROR creating Supabase client: {e}")
    exit(1)

# Test connection by checking the posts table
print("\n" + "="*60)
print("Checking 'posts' table...")
print("="*60)

try:
    # Try to count records
    result = supabase.table("posts").select("id", count="exact").execute()
    
    if hasattr(result, 'count'):
        count = result.count
    elif result.data:
        count = len(result.data)
    else:
        count = 0
    
    print(f"\n✓ Connection successful!")
    print(f"Total records in 'posts' table: {count}")
    
    if count > 0:
        # Get a few sample records
        print("\nFetching sample records...")
        sample = supabase.table("posts").select("id, title").limit(5).execute()
        if sample.data:
            print("\nSample records:")
            for i, record in enumerate(sample.data, 1):
                title = record.get('title', 'N/A')[:50]  # Truncate long titles
                print(f"  {i}. ID: {record.get('id')}, Title: {title}")
    else:
        print("\n⚠ No records found in the 'posts' table.")
        print("This could mean:")
        print("  1. The table is empty (no data inserted yet)")
        print("  2. The table doesn't exist")
        print("  3. There was an error during insertion")
        
        # Check if table exists by trying to get schema
        print("\nChecking if table exists...")
        try:
            # Try a simple query that will fail if table doesn't exist
            test_query = supabase.table("posts").select("id").limit(1).execute()
            print("✓ Table 'posts' exists")
        except Exception as e:
            print(f"❌ Table 'posts' may not exist: {e}")
            print("\nMake sure you've created the table in Supabase:")
            print("""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  embedding vector(768)
);
            """)
    
except Exception as e:
    print(f"\n❌ ERROR querying Supabase: {e}")
    print("\nPossible issues:")
    print("  1. Incorrect PROJECT_URL or SUPABASE_API in .env")
    print("  2. Table 'posts' doesn't exist")
    print("  3. Network/firewall issues")
    print("  4. Supabase project is paused or deleted")

print("\n" + "="*60)

