import sqlite3

def fix_birthday_corruption(db_path):
    """Fix birthday table corruption where Discord IDs are stored in birthday column"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find corrupted records (birthday column looks like Discord ID - very long numbers)
        cursor.execute('SELECT user_id, birthday FROM birthdays WHERE length(birthday) > 10')
        corrupted = cursor.fetchall()
        
        print(f"Found {len(corrupted)} corrupted records:")
        for user_id, birthday in corrupted:
            print(f"  User {user_id}: birthday = {birthday}")
        
        if corrupted:
            # Remove corrupted records
            cursor.execute('DELETE FROM birthdays WHERE length(birthday) > 10')
            conn.commit()
            print(f"Deleted {cursor.rowcount} corrupted records")
        else:
            print("No corrupted records found")
            
        # Show remaining records
        cursor.execute('SELECT COUNT(*) FROM birthdays')
        count = cursor.fetchone()[0]
        print(f"Remaining clean records: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Check both possible database locations
    db_paths = ["./MalaBoT/data/bot.db", "./MalaBoT/bot.db"]
    
    for db_path in db_paths:
        try:
            print(f"\nChecking {db_path}:")
            fix_birthday_corruption(db_path)
        except Exception as e:
            print(f"Could not process {db_path}: {e}")
