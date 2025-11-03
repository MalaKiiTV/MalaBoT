import asyncio
import aiosqlite

async def minimal_test():
    try:
        print("Starting database test...")
        conn = await aiosqlite.connect("test.db")
        print("Connected to database")
        
        await conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
        print("Created table")
        
        await conn.commit()
        print("Committed changes")
        
        await conn.close()
        print("Closed connection")
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(minimal_test())