import asyncio 
import aiosqlite 
 
async def check(): 
    async with aiosqlite.connect('bot.db') as db: 
        cursor = await db.execute('SELECT user_id, xp, level FROM users ORDER BY xp DESC LIMIT 10') 
        rows = await cursor.fetchall() 
        print('User ID              | XP    | Level') 
        print('-' * 45) 
        for uid, xp, lvl in rows: 
            print(f'{uid:20} | {xp:5} | {lvl}') 
 
asyncio.run(check()) 
