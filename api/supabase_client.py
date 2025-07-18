# supabase_client.py
from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

print("[Supabase] SUPABASE_URL:", SUPABASE_URL)
print("[Supabase] SUPABASE_KEY present:", bool(SUPABASE_KEY))
print("[Supabase] SUPABASE_BUCKET_NAME:", SUPABASE_BUCKET_NAME)

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_BUCKET_NAME:
    raise RuntimeError("Supabase environment variables are not set correctly. Check .env file and variable names.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
