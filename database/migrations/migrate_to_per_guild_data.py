import sqlite3
import os
from datetime import datetime
import shutil

def migrate_database():
    db_path = "data/bot.db"
    backup_dir = "backups"
    
    if os.path.exists(db_path):
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = f"{backup_dir}/bot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, backup_path)
        print(f"Backup created: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting migration...")
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_guild_data_new (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL DEFAULT -1,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_xp_time REAL,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_guild_data'")
        if cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO user_guild_data_new (user_id, xp, level, last_xp_time, guild_id) SELECT user_id, xp, level, last_xp_time, -1 FROM user_guild_data")
            cursor.execute("DROP TABLE user_guild_data")
        
        cursor.execute("ALTER TABLE user_guild_data_new RENAME TO user_guild_data")
        print("Migrated user_guild_data")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS birthdays_new (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL DEFAULT -1,
                birthday TEXT NOT NULL,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='birthdays'")
        if cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO birthdays_new (user_id, birthday, guild_id) SELECT user_id, birthday, -1 FROM birthdays")
            cursor.execute("DROP TABLE birthdays")
        
        cursor.execute("ALTER TABLE birthdays_new RENAME TO birthdays")
        print("Migrated birthdays")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings_new (
                warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL DEFAULT -1,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp REAL NOT NULL
            )
        """)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='warnings'")
        if cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO warnings_new SELECT warning_id, user_id, -1, moderator_id, reason, timestamp FROM warnings")
            cursor.execute("DROP TABLE warnings")
        
        cursor.execute("ALTER TABLE warnings_new RENAME TO warnings")
        print("Migrated warnings")
        
        conn.commit()
        print("\nMigration completed!")
        print("IMPORTANT: Existing data has guild_id = -1")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
