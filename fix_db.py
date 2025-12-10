import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Fix the column types - guild_id should be bigint
try:
    result = supabase.rpc('exec_sql', {'sql': 'ALTER TABLE daily_checkins ALTER COLUMN guild_id TYPE bigint;'}).execute()
    print("Successfully altered guild_id to bigint")
except Exception as e:
    print(f"Error: {e}")
