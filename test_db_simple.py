import asyncio
import aiosqlite

class SimpleDatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connection = None

    async def get_connection(self):
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
        return self._connection

    async def initialize_simple(self):
        print("Getting connection...")
        conn = await self.get_connection()
        print("Got connection")
        
        print("Creating settings table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                setting_key TEXT NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, setting_key)
            )
        """)
        print("Created settings table")
        
        await conn.commit()
        print("Committed")
        
        print("Testing get_setting...")
        result = await self.get_setting_simple("test", 12345)
        print(f"Get result: {result}")
        
        print("Testing set_setting...")
        await self.set_setting_simple("test", "test_value", 12345)
        print("Set successful")
        
        result = await self.get_setting_simple("test", 12345)
        print(f"Get after set: {result}")

    async def get_setting_simple(self, key: str, guild_id: int):
        conn = await self.get_connection()
        cursor = await conn.execute("SELECT value FROM settings WHERE setting_key = ? AND guild_id = ?", (key, guild_id))
        result = await cursor.fetchone()
        return result[0] if result else None

    async def set_setting_simple(self, key: str, value: str, guild_id: int):
        conn = await self.get_connection()
        await conn.execute("""
            INSERT OR REPLACE INTO settings (setting_key, value, guild_id, updated_at) 
            VALUES (?, ?, ?, datetime('now'))
        """, (key, value, guild_id))
        await conn.commit()

async def test_simple():
    try:
        print("Starting simple database test...")
        db = SimpleDatabaseManager("simple_test.db")
        await db.initialize_simple()
        print("Simple test completed!")
    except Exception as e:
        print(f"Error in simple test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())