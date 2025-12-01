"""Fix all user levels based on their current XP."""
import asyncio
import aiosqlite
from config.constants import XP_TABLE

def calculate_level(xp: int) -> int:
    """Calculate level from total XP."""
    if xp < 0:
        return 1
    
    level = 1
    # Sort levels in descending order and find the highest level we qualify for
    for lvl in sorted(XP_TABLE.keys(), reverse=True):
        if xp >= XP_TABLE[lvl]:
            level = lvl
            break
    
    return level

async def fix_all_levels():
    """Recalculate and fix all user levels."""
    async with aiosqlite.connect('data/bot.db') as db:
        # Get all users
        cursor = await db.execute("SELECT user_id, xp FROM users")
        users = await cursor.fetchall()
        
        print(f"Found {len(users)} users to fix...")
        
        for user_id, xp in users:
            correct_level = calculate_level(xp)
            await db.execute(
                "UPDATE users SET level = ? WHERE user_id = ?",
                (correct_level, user_id)
            )
            print(f"User {user_id}: {xp} XP -> Level {correct_level}")
        
        await db.commit()
        print("\n✅ All levels fixed!")

if __name__ == "__main__":
    asyncio.run(fix_all_levels())
