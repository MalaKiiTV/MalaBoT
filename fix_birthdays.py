import sqlite3
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

sqlite_conn = sqlite3.connect('data/bot.db')
sqlite_cursor = sqlite_conn.cursor()

guild_id = 542004156513255445

print("🔄 Fixing birthday data...\n")

# First, let's see what we have
sqlite_cursor.execute("SELECT user_id, birthday, timezone, announced_year FROM birthdays")
birthdays = sqlite_cursor.fetchall()

print("Current birthdays in SQLite:")
for row in birthdays:
    print(f"  User {row[0]}: {row[1]}")

print("\n" + "="*50)
print("We need to store birthdays as MM-DD format.")
print("Supabase requires a DATE type, so we'll use a dummy year (2000).")
print("Your bot code will only display MM-DD to users.")
print("="*50 + "\n")

for user_id, birthday, timezone, announced_year in birthdays:
    if birthday:
        try:
            # If it's already MM-DD format, convert to full date
            if len(birthday.split('-')) == 2:
                month, day = birthday.split('-')
                full_date = f"2000-{month.zfill(2)}-{day.zfill(2)}"
            else:
                # Already a full date
                full_date = birthday
            
            data = {
                'user_id': user_id,
                'guild_id': guild_id,
                'birthday': full_date,
                'timezone': timezone or 'UTC',
                'announced_year': announced_year
            }
            
            supabase.table('birthdays').insert(data).execute()
            print(f"✅ Migrated birthday for user {user_id}: {birthday}")
        except Exception as e:
            print(f"❌ Error for user {user_id}: {e}")

print("\n✅ Birthday migration complete!")
print("\n📝 Note: Birthdays are stored with year 2000, but your bot will only show MM-DD to users")

sqlite_conn.close()
