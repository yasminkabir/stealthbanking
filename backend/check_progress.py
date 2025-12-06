"""
Quick script to check embedding progress in Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("PROJECT_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    result = supabase.table("posts").select("id", count="exact").execute()
    count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
    
    print("="*60)
    print("Embedding Progress Check")
    print("="*60)
    print(f"Total records in database: {count}")
    print(f"\nThe embedding script will automatically resume from row {count + 1}")
    print("="*60)
except Exception as e:
    print(f"Error: {e}")


