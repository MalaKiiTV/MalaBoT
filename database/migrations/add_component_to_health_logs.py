import sqlite3
import os
import sys

# This allows the script to find your settings file
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from config.settings import settings


def migrate():
    """
    Ensures 'component', 'status', 'value', and 'details' columns exist in 'health_logs'.
    """
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    print(f"Connecting to database at: {db_path}")

    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(health_logs)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Existing columns in health_logs: {columns}")

        # --- Check for ALL required columns ---
        required_cols = {
            "component": "TEXT",
            "status": "TEXT",
            "value": "REAL",
            "details": "TEXT",
        }

        for col_name, col_type in required_cols.items():
            if col_name not in columns:
                print(f"Adding '{col_name}' column...")
                cursor.execute(
                    f"ALTER TABLE health_logs ADD COLUMN {col_name} {col_type}"
                )
                print(f"Successfully added '{col_name}' column.")
            else:
                print(f"Column '{col_name}' already exists.")

        conn.commit()
        conn.close()
        print("Migration verification completed successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred during migration: {e}")


if __name__ == "__main__":
    migrate()
