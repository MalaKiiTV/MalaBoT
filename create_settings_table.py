import sqlite3
import os

def create_settings_table():
    """Create the settings table directly using sqlite3."""
    db_path = 'data/bot.db'
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, setting_key)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Settings table created successfully in {db_path}!")
        print(f"Database location: {os.path.abspath(db_path)}")
        
        # Verify it was created
        conn = sqlite3.connect('bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            print("✅ Settings table verified to exist!")
        else:
            print("❌ Settings table was not created!")
            
    except Exception as e:
        print(f"❌ Error creating settings table: {e}")

if __name__ == "__main__":
    create_settings_table()