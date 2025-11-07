#!/usr/bin/env python3
"""
Fix verification database issues and ensure proper flow
"""

import sqlite3
import os
import sys

def fix_database_schema():
    """Ensure all database files have correct schema"""
    db_paths = [
        './data/bot.db',
        './bot.db'
    ]
    
    fixed_count = 0
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"Checking {db_path}...")
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='verifications'
                """)
                
                if not cursor.fetchone():
                    print(f"Creating verifications table in {db_path}")
                    cursor.execute("""
                        CREATE TABLE verifications (
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
                    """)
                    conn.commit()
                    fixed_count += 1
                else:
                    # Check if discord_id column exists
                    cursor.execute('PRAGMA table_info(verifications)')
                    columns = cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    
                    if 'discord_id' not in column_names:
                        print(f"Adding discord_id column to {db_path}")
                        cursor.execute('ALTER TABLE verifications ADD COLUMN discord_id INTEGER')
                        conn.commit()
                        fixed_count += 1
                    else:
                        print(f"{db_path} schema is OK")
                
                conn.close()
                
            except Exception as e:
                print(f"Error fixing {db_path}: {e}")
        else:
            print(f"{db_path} does not exist")
    
    return fixed_count

def main():
    print("=== Verification Database Fix ===")
    
    # Fix all database schemas
    fixed = fix_database_schema()
    
    if fixed > 0:
        print(f"✅ Fixed {fixed} database schema issues")
    else:
        print("✅ All database schemas are already correct")
    
    print("\n=== Database Fix Complete ===")
    print("Restart your bot and the verification system should work!")

if __name__ == "__main__":
    main()
