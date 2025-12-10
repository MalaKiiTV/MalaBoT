import asyncio 
from src.database.supabase_models import DatabaseManager 
import json 
 
async def main(): 
    db = DatabaseManager() 
    await db.initialize() 
    guild_id = 542004156513255445 
    data = await db.get_setting('protected_roles', guild_id) 
    print(f'Current protected roles: {data}') 
    if data: 
        roles = json.loads(data) if isinstance(data, str) else data 
        print(f'Parsed: {roles}') 
        if 1447377757230338098 in roles: 
            roles.remove(1447377757230338098) 
            await db.set_setting('protected_roles', json.dumps(roles), guild_id) 
            print(f'Updated to: {roles}') 
 
asyncio.run(main()) 
