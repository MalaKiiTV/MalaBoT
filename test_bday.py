import asyncio 
from database.models import DatabaseManager 
 
async def test(): 
    db = DatabaseManager('data/bot.db') 
    await db.initialize() 
    result = await db.set_user_birthday(123456789, '09-16') 
    print('Set result:', result) 
    cursor = await (await db.get_connection()).execute('SELECT * FROM birthdays') 
    print('After set:', await cursor.fetchall()) 
 
asyncio.run(test()) 
