import asyncio
import aiosqlite


async def reset_all_xp():
    async with aiosqlite.connect("data/bot.db") as db:
        await db.execute("UPDATE users SET xp = 0, level = 1")
        await db.commit()
        print("✅ All XP reset to 0!")


asyncio.run(reset_all_xp())
