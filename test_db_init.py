import asyncio
from database.models import DatabaseManager

async def test_db_init():
    try:
        db = DatabaseManager("bot.db")
        await db.initialize()
        print("Database initialized successfully")
        
        # Test if we can use get_setting
        result = await db.get_setting("test_key", 12345)
        print(f"get_setting test result: {result}")
        
        # Test if we can use set_setting
        await db.set_setting("test_key", "test_value", 12345)
        print("set_setting test successful")
        
        # Test getting the value back
        result = await db.get_setting("test_key", 12345)
        print(f"get_setting after set_setting: {result}")
        
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db_init())