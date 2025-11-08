import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# List all tables
print("\n=== Tables in Database ===")
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
for t in tables:
    print("-", t[0])

# For each table, show columns
print("\n=== Table Columns ===")
for t in tables:
    table_name = t[0]
    print(f"\nTable: {table_name}")
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        for col in cursor.fetchall():
            print(f"  {col[1]} ({col[2]})")
    except Exception as e:
        print("  Error reading:", e)

conn.close()
