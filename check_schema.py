import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect('postgresql://malabot:Vhagar123!@localhost/malabot')
    result = await conn.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'daily_checkins' ORDER BY ordinal_position")
    for r in result:
        print(f"{r['column_name']}: {r['data_type']}")
    await conn.close()

asyncio.run(check())
