import sqlite3
import os

def check_database():
    """Check if the settings table exists and show its schema."""
    db_path = 'data/bot.db'
    
    print(f"Checking database at: {os.path.abspath(db_path)}")
    print(f"Database file exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Settings table exists!")
            
            # Show schema
            cursor.execute("PRAGMA table_info(settings)")
            columns = cursor.fetchall()
            print("\nSettings table schema:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
                
            # Show all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = cursor.fetchall()
            print(f"\nAll tables in database: {[t[0] for t in all_tables]}")
            
        else:
            print("❌ Settings table does not exist!")
            
            # Show all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = cursor.fetchall()
            print(f"Existing tables: {[t[0] for t in all_tables]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()