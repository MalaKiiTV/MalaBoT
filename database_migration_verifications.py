#!/usr/bin/env python3
"""
Migration script to fix verifications table schema
Changes from old schema to new schema expected by verification code
"""

import sqlite3
import sys

def migrate_verifications_table():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(verifications)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Create new table with correct schema
        cursor.execute('''
            CREATE TABLE verifications_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id INTEGER NOT NULL,
                activision_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                screenshot_url TEXT,
                status TEXT DEFAULT 'pending',
                reviewed_by INTEGER,
                reviewed_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migrate any existing data if old table exists and has user_id
        if 'user_id' in columns:
            print("Migrating existing data...")
            cursor.execute('''
                INSERT INTO verifications_new (discord_id, created_at)
                SELECT user_id, created_at FROM verifications
                WHERE user_id IS NOT NULL
            ''')
        
        # Drop old table and rename new one
        cursor.execute('DROP TABLE verifications')
        cursor.execute('ALTER TABLE verifications_new RENAME TO verifications')
        
        conn.commit()
        print("✅ Verifications table migrated successfully!")
        
        # Show new schema
        cursor.execute("PRAGMA table_info(verifications)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"New columns: {new_columns}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    if migrate_verifications_table():
        print("🎉 Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
