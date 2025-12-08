import os
import sqlite3
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Connect to both databases
sqlite_conn = sqlite3.connect('data/bot.db')
sqlite_cursor = sqlite_conn.cursor()

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

print("🔄 Starting migration to Supabase...\n")

# SQL to create tables in Supabase (with guild_id added where needed)
create_tables_sql = """
-- Users table (now per-guild)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    username TEXT,
    discriminator TEXT,
    display_name TEXT,
    avatar_url TEXT,
    joined_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP,
    is_bot BOOLEAN DEFAULT FALSE,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    kick_count INTEGER DEFAULT 0,
    ban_count INTEGER DEFAULT 0,
    is_muted BOOLEAN DEFAULT FALSE,
    muted_until TIMESTAMP,
    mute_reason TEXT,
    reputation INTEGER DEFAULT 0,
    bio TEXT,
    birthday DATE,
    currency_balance INTEGER DEFAULT 0,
    last_daily TIMESTAMP,
    last_work TIMESTAMP,
    last_xp_gain TIMESTAMP,
    xp_multiplier REAL DEFAULT 1.0,
    custom_title TEXT,
    premium_expires TIMESTAMP,
    is_premium BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, guild_id)
);

-- Birthdays table (now per-guild)
CREATE TABLE IF NOT EXISTS birthdays (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    birthday DATE NOT NULL,
    timezone TEXT DEFAULT 'UTC',
    announced_year INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, guild_id)
);

-- Settings table (already has guild_id)
CREATE TABLE IF NOT EXISTS settings (
    id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    setting_key TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(guild_id, setting_key)
);

-- Mod logs (already has guild_id)
CREATE TABLE IF NOT EXISTS mod_logs (
    id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    action TEXT NOT NULL,
    reason TEXT,
    duration INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Roast XP (global config - no guild_id needed)
CREATE TABLE IF NOT EXISTS roast_xp (
    id BIGSERIAL PRIMARY KEY,
    action TEXT NOT NULL UNIQUE,
    base_xp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Roast log (now per-guild)
CREATE TABLE IF NOT EXISTS roast_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    target_id BIGINT,
    action TEXT NOT NULL,
    xp_gained INTEGER DEFAULT 0,
    message_content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit log (already has guild_id)
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    category TEXT,
    action TEXT NOT NULL,
    user_id BIGINT,
    target_id BIGINT,
    channel_id BIGINT,
    details TEXT,
    guild_id BIGINT
);

-- Health logs (global - no guild_id needed)
CREATE TABLE IF NOT EXISTS health_logs (
    id BIGSERIAL PRIMARY KEY,
    cpu_usage REAL,
    memory_usage REAL,
    disk_usage REAL,
    uptime INTEGER,
    guild_count INTEGER,
    user_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    component TEXT,
    value REAL,
    status TEXT,
    details TEXT
);

-- System flags (global - no guild_id needed)
CREATE TABLE IF NOT EXISTS system_flags (
    id BIGSERIAL PRIMARY KEY,
    flag_name TEXT NOT NULL UNIQUE,
    flag_value BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Appeals (already has guild_id)
CREATE TABLE IF NOT EXISTS appeals (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    appeal_text TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT NOW(),
    reviewed_by BIGINT,
    reviewed_at TIMESTAMP,
    review_notes TEXT
);

-- Level roles (already has guild_id)
CREATE TABLE IF NOT EXISTS level_roles (
    id BIGSERIAL PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    level INTEGER NOT NULL,
    role_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(guild_id, level)
);

-- Daily checkins (now per-guild)
CREATE TABLE IF NOT EXISTS daily_checkins (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    last_checkin DATE,
    checkin_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, guild_id)
);

-- Verifications (now per-guild)
CREATE TABLE IF NOT EXISTS verifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    activision_id TEXT,
    platform TEXT,
    screenshot_url TEXT,
    status TEXT DEFAULT 'pending',
    reviewed_by BIGINT,
    reviewed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_user_guild ON users(user_id, guild_id);
CREATE INDEX IF NOT EXISTS idx_birthdays_user_guild ON birthdays(user_id, guild_id);
CREATE INDEX IF NOT EXISTS idx_settings_guild ON settings(guild_id);
CREATE INDEX IF NOT EXISTS idx_mod_logs_guild ON mod_logs(guild_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_guild ON audit_log(guild_id);
CREATE INDEX IF NOT EXISTS idx_level_roles_guild ON level_roles(guild_id);
"""

print("📋 Creating tables in Supabase...")
print("⚠️  Note: You need to run this SQL in Supabase SQL Editor:")
print("\n" + "="*60)
print(create_tables_sql)
print("="*60 + "\n")

print("Instructions:")
print("1. Go to https://supabase.com/dashboard/project/nukapipoueavsdsvkjev/sql/new")
print("2. Copy the SQL above")
print("3. Paste it into the SQL Editor")
print("4. Click 'Run'")
print("5. Come back here and type 'done' when finished")

response = input("\nType 'done' when you've created the tables: ")

if response.lower() != 'done':
    print("❌ Migration cancelled")
    exit()

print("\n✅ Tables created! Now migrating data...\n")

# Get your guild ID (you'll need to provide this)
guild_id = input("Enter your Discord server/guild ID: ")

# Migrate data with guild_id
def migrate_table(table_name, add_guild_id=False):
    try:
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        columns = [description[0] for description in sqlite_cursor.description]
        
        if not rows:
            print(f"  ⚠️  {table_name}: No data to migrate")
            return
        
        for row in rows:
            data = dict(zip(columns, row))
            
            # Add guild_id if needed
            if add_guild_id and 'guild_id' not in data:
                data['guild_id'] = guild_id
            
            # Convert datetime strings to proper format
            for key, value in data.items():
                if value and ('_at' in key or key == 'birthday'):
                    try:
                        if isinstance(value, str):
                            data[key] = value
                    except:
                        pass
            
            # Remove id if it exists (let Supabase auto-generate)
            if 'id' in data:
                del data['id']
            
            supabase.table(table_name).insert(data).execute()
        
        print(f"  ✅ {table_name}: Migrated {len(rows)} rows")
    except Exception as e:
        print(f"  ❌ {table_name}: Error - {str(e)}")

# Migrate each table
print("🔄 Migrating data...\n")

migrate_table('users', add_guild_id=True)
migrate_table('birthdays', add_guild_id=True)
migrate_table('settings')  # Already has guild_id
migrate_table('mod_logs')  # Already has guild_id
migrate_table('roast_xp')  # Global config
migrate_table('roast_log', add_guild_id=True)
migrate_table('audit_log')  # Already has guild_id
migrate_table('appeals')  # Already has guild_id
migrate_table('level_roles')  # Already has guild_id
migrate_table('daily_checkins', add_guild_id=True)
migrate_table('verifications', add_guild_id=True)

print("\n✅ Migration complete!")
print("\n📝 Next steps:")
print("1. Test your bot locally")
print("2. If it works, update the droplet")
print("3. Delete the old SQLite database files")

sqlite_conn.close()
