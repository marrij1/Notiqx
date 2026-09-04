import os

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase environment variables are missing.")


# Client used for authentication operations
supabase_auth: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# Separate client used for backend database operations
supabase_db: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)