import sqlite3
import os

def migrate_settings_table():
    """Migrate existing settings table to correct schema."""
    db_path = 'data/bot.db'
    
    print(f"Migrating database at: {os.path.abspath(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(settings)")
        current_columns = cursor.fetchall()
        print("Current settings table columns:")
        for col in current_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Get existing data
        cursor.execute("SELECT * FROM settings")
        existing_data = cursor.fetchall()
        print(f"\nFound {len(existing_data)} existing settings to migrate")
        
        # Drop the old table
        cursor.execute("DROP TABLE settings")
        print("Dropped old settings table")
        
        # Create new table with correct schema
        cursor.execute('''
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, setting_key)
            )
        ''')
        print("Created new settings table with correct schema")
        
        # If there was existing data, we need to migrate it
        # Since old table had key/value and new needs guild_id/setting_key/value
        # We'll assume old data was for guild_id 1 and map key -> setting_key
        if existing_data:
            for row in existing_data:
                old_key, old_value, old_updated = row
                cursor.execute('''
                    INSERT INTO settings (guild_id, setting_key, value, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (1, old_key, old_value, old_updated))
            print("Migrated existing data to new schema")
        
        conn.commit()
        
        # Verify new schema
        cursor.execute("PRAGMA table_info(settings)")
        new_columns = cursor.fetchall()
        print("\nNew settings table columns:")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_settings_table()