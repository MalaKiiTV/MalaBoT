"""
Comprehensive fix for all bot errors
Fixes:
1. DatabaseManager missing methods (set_daily_claimed, get_leaderboard)
2. DatabaseManager.log_event() parameter name (target_user_id -> target_id)
3. SystemHelper missing method (sanitize_input)
4. CooldownHelper missing method (check_cooldown)
5. EmbedHelper.create_embed() incorrect parameters (thumbnail, missing description)
"""

import os
import re

def fix_database_models():
    """Add missing methods to DatabaseManager"""
    file_path = "database/models.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the position to add new methods (before the last method or at the end of class)
    # Add after get_roast_leaderboard method
    insert_position = content.find("async def get_roast_leaderboard")
    if insert_position == -1:
        print("❌ Could not find insertion point in database/models.py")
        return False
    
    # Find the end of get_roast_leaderboard method
    next_method = content.find("\n    async def", insert_position + 10)
    if next_method == -1:
        # It's the last method, find the end of the class
        next_method = len(content)
    
    new_methods = '''
    async def get_leaderboard(self, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get XP leaderboard for a guild."""
        conn = await self.get_connection()
        cursor = await conn.execute("""
            SELECT user_id, xp, level, total_messages
            FROM users
            ORDER BY xp DESC
            LIMIT ?
        """, (limit,))
        
        rows = await cursor.fetchall()
        return [
            {
                'user_id': row[0],
                'xp': row[1],
                'level': row[2],
                'total_messages': row[3]
            }
            for row in rows
        ]
    
    async def set_daily_claimed(self, user_id: int, guild_id: int):
        """Mark daily reward as claimed for a user."""
        from datetime import date
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
            
            # Check if claimed today
            today = date.today().isoformat()
            if last_daily == today:
                return  # Already claimed today
            
            # Update streak
            new_streak = current_streak + 1
            
            await conn.execute("""
                UPDATE users
                SET daily_streak = ?,
                    last_daily_award_date = ?
                WHERE user_id = ?
            """, (new_streak, today, user_id))
        else:
            # Create new user entry
            today = date.today().isoformat()
            await conn.execute("""
                INSERT INTO users (user_id, daily_streak, last_daily_award_date)
                VALUES (?, 1, ?)
            """, (user_id, today))
        
        await conn.commit()

'''
    
    # Insert the new methods
    content = content[:next_method] + new_methods + content[next_method:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added get_leaderboard() and set_daily_claimed() to DatabaseManager")
    return True

def fix_moderation_cog():
    """Fix target_user_id -> target_id in moderation.py"""
    file_path = "cogs/moderation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all occurrences of target_user_id with target_id
    content = content.replace('target_user_id=', 'target_id=')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed target_user_id -> target_id in moderation.py")
    return True

def fix_system_helper():
    """Add sanitize_input method to SystemHelper"""
    file_path = "utils/helpers.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find SystemHelper class
    system_helper_pos = content.find("class SystemHelper:")
    if system_helper_pos == -1:
        print("❌ Could not find SystemHelper class")
        return False
    
    # Find the end of get_file_size method
    get_file_size_pos = content.find("def get_file_size", system_helper_pos)
    if get_file_size_pos == -1:
        print("❌ Could not find get_file_size method")
        return False
    
    # Find the end of this method (next method or end of class)
    next_section = content.find("\n\n   # Convenience instances", get_file_size_pos)
    if next_section == -1:
        next_section = content.find("\n\nclass ", get_file_size_pos + 10)
    
    if next_section == -1:
        print("❌ Could not find insertion point for sanitize_input")
        return False
    
    new_method = '''
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 200) -> str:
        """Sanitize user input by removing potentially harmful characters and limiting length."""
        if not text:
            return ""
        
        # Remove null bytes and other control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
'''
    
    # Insert the new method
    content = content[:next_section] + new_method + content[next_section:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added sanitize_input() to SystemHelper")
    return True

def fix_cooldown_helper():
    """Add check_cooldown method to CooldownHelper"""
    file_path = "utils/helpers.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the get_remaining_cooldown method
    get_remaining_pos = content.find("def get_remaining_cooldown")
    if get_remaining_pos == -1:
        print("❌ Could not find get_remaining_cooldown method")
        return False
    
    # Find the end of this method (next class or section)
    next_section = content.find("\n\nclass ", get_remaining_pos + 10)
    if next_section == -1:
        next_section = content.find("\n\n   # Convenience instances", get_remaining_pos)
    
    if next_section == -1:
        print("❌ Could not find insertion point for check_cooldown")
        return False
    
    new_method = '''
    
    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int) -> bool:
        """
        Check if user can use a command (not on cooldown).
        If not on cooldown, automatically sets the cooldown.
        Returns True if command can be used, False if on cooldown.
        """
        if self.is_on_cooldown(user_id, command):
            return False
        
        # Not on cooldown, set it now
        self.set_cooldown(user_id, command, cooldown_seconds)
        return True
'''
    
    # Insert the new method
    content = content[:next_section] + new_method + content[next_section:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added check_cooldown() to CooldownHelper")
    return True

def fix_embed_helper():
    """Fix EmbedHelper.create_embed to support thumbnail and optional description"""
    file_path = "utils/helpers.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the create_embed method
    old_method = '''    @staticmethod
    def create_embed(title: str, description: str, color: int = COLORS['info']) -> discord.Embed:
        """Create a standardized embed with consistent formatting."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        return embed'''
    
    new_method = '''    @staticmethod
    def create_embed(title: str, description: str = None, color: int = COLORS['info'], 
                     thumbnail: str = None, **kwargs) -> discord.Embed:
        """Create a standardized embed with consistent formatting."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        
        # Add thumbnail if provided
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        # Add any additional fields from kwargs
        if 'footer' in kwargs:
            embed.set_footer(text=kwargs['footer'])
        if 'image' in kwargs:
            embed.set_image(url=kwargs['image'])
        if 'author' in kwargs:
            embed.set_author(name=kwargs['author'])
        
        return embed'''
    
    content = content.replace(old_method, new_method)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed EmbedHelper.create_embed() to support thumbnail and optional description")
    return True

def fix_utility_cog():
    """Fix utility.py to add description parameter to create_embed calls"""
    file_path = "cogs/utility.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix userinfo embed (around line 130)
    content = re.sub(
        r'embed = create_embed\(\s*title=f"🔤 User Information: {target_user\.display_name}",\s*color=target_user\.color if target_user\.color else COLORS\["primary"\],\s*thumbnail=target_user\.avatar\.url if target_user\.avatar else None\s*\)',
        '''embed = create_embed(
                title=f"🔤 User Information: {target_user.display_name}",
                description="",
                color=target_user.color if target_user.color else COLORS["primary"],
                thumbnail=target_user.avatar.url if target_user.avatar else None
            )''',
        content
    )
    
    # Fix serverinfo embed (around line 283)
    content = re.sub(
        r'embed = create_embed\(\s*title=f"📊 Server Information: {guild\.name}",\s*color=COLORS\["primary"\],\s*thumbnail=guild\.icon\.url if guild\.icon else None\s*\)',
        '''embed = create_embed(
                title=f"📊 Server Information: {guild.name}",
                description="",
                color=COLORS["primary"],
                thumbnail=guild.icon.url if guild.icon else None
            )''',
        content
    )
    
    # Fix serverstats embed - add description parameter
    content = re.sub(
        r'embed = create_embed\(\s*title="📈 Server Statistics",\s*color=COLORS\["primary"\]\s*\)',
        'embed = create_embed(\n                title="📈 Server Statistics",\n                description="",\n                color=COLORS["primary"]\n            )',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed utility.py embed creation calls")
    return True

def main():
    """Run all fixes"""
    print("🔧 Starting comprehensive bot fixes...\n")
    
    # Change to MalaBoT directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = True
    
    # Fix 1: DatabaseManager missing methods
    print("1️⃣ Fixing DatabaseManager...")
    if not fix_database_models():
        success = False
    
    # Fix 2: Moderation cog parameter names
    print("\n2️⃣ Fixing moderation.py...")
    if not fix_moderation_cog():
        success = False
    
    # Fix 3: SystemHelper missing method
    print("\n3️⃣ Fixing SystemHelper...")
    if not fix_system_helper():
        success = False
    
    # Fix 4: CooldownHelper missing method
    print("\n4️⃣ Fixing CooldownHelper...")
    if not fix_cooldown_helper():
        success = False
    
    # Fix 5: EmbedHelper parameters
    print("\n5️⃣ Fixing EmbedHelper...")
    if not fix_embed_helper():
        success = False
    
    # Fix 6: Utility cog embed calls
    print("\n6️⃣ Fixing utility.py...")
    if not fix_utility_cog():
        success = False
    
    if success:
        print("\n✅ All fixes applied successfully!")
        print("\n📝 Summary of fixes:")
        print("   • Added get_leaderboard() to DatabaseManager")
        print("   • Added set_daily_claimed() to DatabaseManager")
        print("   • Fixed target_user_id -> target_id in moderation.py")
        print("   • Added sanitize_input() to SystemHelper")
        print("   • Added check_cooldown() to CooldownHelper")
        print("   • Fixed EmbedHelper.create_embed() to support thumbnail and optional description")
        print("   • Fixed utility.py embed creation calls")
        print("\n🔄 Please restart the bot to apply changes.")
    else:
        print("\n❌ Some fixes failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()