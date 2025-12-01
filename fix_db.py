import sqlite3

conn = sqlite3.connect("bot.db")
c = conn.cursor()

# Rename old table
c.execute("ALTER TABLE settings RENAME TO tmp_settings")

# Create new table with the correct column name
c.execute(
    """
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT,
    guild_id INTEGER,
    updated_at TEXT,
    UNIQUE(guild_id, key)
)
"""
)

# Copy data from old table
c.execute(
    """
INSERT INTO settings (id, key, value, guild_id, updated_at)
SELECT id, key, value, guild_id, updated_at FROM tmp_settings
"""
)

# Drop old table
c.execute("DROP TABLE tmp_settings")

conn.commit()
conn.close()

print("Database column renamed successfully!")
