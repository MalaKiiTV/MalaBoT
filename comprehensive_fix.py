"""
Comprehensive fix for ALL remaining bot errors
This script fixes the actual issues found in the logs
"""

import os

def fix_helpers():
    """Fix all helper methods"""
    file_path = "utils/helpers.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix calculate_level_from_xp - it's being called with only total_xp, not xp_table
    # The method should get xp_table from config
    old_calc = '''    @staticmethod
    def calculate_level_from_xp(total_xp: int, xp_table: Dict[int, int]) -> int:
        """Calculate level from total XP using the XP table."""
        level = 1
        for lvl, xp_required in sorted(xp_table.items()):
            if total_xp >= xp_required:
                level = lvl
            else:
                break
        return level'''
    
    new_calc = '''    @staticmethod
    def calculate_level_from_xp(total_xp: int, xp_table: Dict[int, int] = None) -> int:
        """Calculate level from total XP using the XP table."""
        if xp_table is None:
            # Import here to avoid circular dependency
            from config.constants import XP_TABLE
            xp_table = XP_TABLE
        
        level = 1
        for lvl, xp_required in sorted(xp_table.items()):
            if total_xp >= xp_required:
                level = lvl
            else:
                break
        return level'''
    
    content = content.replace(old_calc, new_calc)
    
    # 2. Fix set_cooldown - it's being called with only 2 args (user_id, command) but needs 3
    # The cooldown duration should come from config
    old_set = '''    def set_cooldown(self, user_id: int, command: str, seconds: int):
        """Set a cooldown for a user on a command."""
        key = f"{user_id}_{command}"
        self.cooldowns[key] = datetime.now() + timedelta(seconds=seconds)'''
    
    new_set = '''    def set_cooldown(self, user_id: int, command: str, seconds: int = None):
        """Set a cooldown for a user on a command."""
        if seconds is None:
            # Import here to avoid circular dependency
            from config.constants import COMMAND_COOLDOWNS
            seconds = COMMAND_COOLDOWNS.get(command, 5)
        
        key = f"{user_id}_{command}"
        self.cooldowns[key] = datetime.now() + timedelta(seconds=seconds)'''
    
    content = content.replace(old_set, new_set)
    
    # 3. Add get_discord_timestamp method to TimeHelper
    timestamp_method = '''
    @staticmethod
    def get_discord_timestamp(dt: datetime, style: str = "R") -> str:
        """
        Convert datetime to Discord timestamp format.
        Styles: t (short time), T (long time), d (short date), D (long date),
                f (short datetime), F (long datetime), R (relative)
        """
        if dt is None:
            return "Unknown"
        
        timestamp = int(dt.timestamp())
        return f"<t:{timestamp}:{style}>"
'''
    
    # Find TimeHelper class and add method after format_duration
    time_helper_pos = content.find("class TimeHelper:")
    format_duration_end = content.find("class PermissionHelper:", time_helper_pos)
    
    if time_helper_pos != -1 and format_duration_end != -1:
        content = content[:format_duration_end] + timestamp_method + "\n" + content[format_duration_end:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed helpers.py")

def fix_database():
    """Add increment_daily_streak method to DatabaseManager"""
    file_path = "database/models.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add increment_daily_streak method after set_daily_claimed
    increment_method = '''
    async def increment_daily_streak(self, user_id: int, guild_id: int) -> int:
        """Increment and return the user's daily streak."""
        from datetime import date, timedelta
        conn = await self.get_connection()
        
        # Get current user data
        cursor = await conn.execute("""
            SELECT daily_streak, last_daily_award_date
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        
        row = await cursor.fetchone()
        
        if row:
            current_streak = row[0] or 0
            last_daily = row[1]
            
            # Check if streak should continue
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            if last_daily:
                last_date = date.fromisoformat(last_daily)
                if last_date == yesterday:
                    # Streak continues
                    new_streak = current_streak + 1
                elif last_date == today:
                    # Already claimed today
                    new_streak = current_streak
                else:
                    # Streak broken
                    new_streak = 1
            else:
                new_streak = 1
            
            await conn.execute("""
                UPDATE users
                SET daily_streak = ?
                WHERE user_id = ?
            """, (new_streak, user_id))
            await conn.commit()
            
            return new_streak
        else:
            return 1
'''
    
    # Find set_daily_claimed and add after it
    set_daily_pos = content.find("async def set_daily_claimed")
    if set_daily_pos != -1:
        # Find the end of set_daily_claimed method
        next_method = content.find("\n    async def", set_daily_pos + 10)
        if next_method != -1:
            content = content[:next_method] + increment_method + content[next_method:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed database/models.py")

def fix_moderation():
    """Add asyncio import to moderation.py"""
    file_path = "cogs/moderation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if asyncio is already imported
    if 'import asyncio' not in content:
        # Add after discord import
        content = content.replace('import discord\n', 'import discord\nimport asyncio\n')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed moderation.py - added asyncio import")
    else:
        print("✅ moderation.py already has asyncio import")

def main():
    """Run all fixes"""
    print("🔧 Applying comprehensive fixes...\n")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    fix_helpers()
    fix_database()
    fix_moderation()
    
    print("\n✅ All fixes applied!")
    print("\n📝 Fixed issues:")
    print("   1. XPHelper.calculate_level_from_xp() - now uses XP_TABLE from config")
    print("   2. CooldownHelper.set_cooldown() - now uses COMMAND_COOLDOWNS from config")
    print("   3. TimeHelper.get_discord_timestamp() - added method")
    print("   4. DatabaseManager.increment_daily_streak() - added method")
    print("   5. moderation.py - added asyncio import")

if __name__ == "__main__":
    main()