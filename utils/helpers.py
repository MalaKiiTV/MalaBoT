"""
Helper functions and utilities for MalaBoT.
Contains embed creators, time utilities, permission checks, and more.
"""

import discord
from datetime import datetime, timedelta
from typing import Optional, List, Union, Dict, Any
import asyncio
import psutil
import os
from config.constants import COLORS, ERROR_MESSAGES, SUCCESS_MESSAGES, LEVEL_ROLE_MAP
from config.settings import settings

class EmbedHelper:
    """Helper class for creating consistent embeds."""
    
    @staticmethod
    def create_embed(title: str, description: str = None, color: int = COLORS["primary"],
                    footer: str = None, thumbnail: str = None, image: str = None,
                    author_name: str = None, author_icon: str = None,
                    fields: List[tuple] = None) -> discord.Embed:
        """Create a standardized embed."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if footer:
            embed.set_footer(text=footer)
        else:
            embed.set_footer(text=f"MalaBoT • v{settings.BOT_VERSION}")
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if image:
            embed.set_image(url=image)
        
        if author_name:
            embed.set_author(name=author_name, icon_url=author_icon)
        
        if fields:
            for name, value, inline in fields:
                if name and value:
                    embed.add_field(name=name, value=value, inline=inline)
        
        return embed
    
    @staticmethod
    def success_embed(title: str, description: str = None) -> discord.Embed:
        """Create a success embed."""
        return EmbedHelper.create_embed(
            title=f"✅ {title}",
            description=description,
            color=COLORS["success"]
        )
    
    @staticmethod
    def error_embed(title: str, description: str = None) -> discord.Embed:
        """Create an error embed."""
        return EmbedHelper.create_embed(
            title=f"❌ {title}",
            description=description,
            color=COLORS["error"]
        )
    
    @staticmethod
    def warning_embed(title: str, description: str = None) -> discord.Embed:
        """Create a warning embed."""
        return EmbedHelper.create_embed(
            title=f"⚠️ {title}",
            description=description,
            color=COLORS["warning"]
        )
    
    @staticmethod
    def info_embed(title: str, description: str = None) -> discord.Embed:
        """Create an info embed."""
        return EmbedHelper.create_embed(
            title=f"ℹ️ {title}",
            description=description,
            color=COLORS["info"]
        )
    
    @staticmethod
    def xp_embed(title: str, description: str = None, user: discord.Member = None) -> discord.Embed:
        """Create an XP-themed embed."""
        author_name = user.display_name if user else None
        author_icon = user.avatar.url if user and user.avatar else None
        
        return EmbedHelper.create_embed(
            title=f"🏆 {title}",
            description=description,
            color=COLORS["xp"],
            author_name=author_name,
            author_icon=author_icon
        )
    
    @staticmethod
    def birthday_embed(title: str, description: str = None, user: discord.Member = None) -> discord.Embed:
        """Create a birthday-themed embed."""
        return EmbedHelper.create_embed(
            title=f"🎂 {title}",
            description=description,
            color=COLORS["birthday"]
        )
    
    @staticmethod
    def welcome_embed(title: str, description: str = None, user: discord.Member = None,
                     image_url: str = None) -> discord.Embed:
        """Create a welcome embed."""
        thumbnail = user.avatar.url if user and user.avatar else None
        
        return EmbedHelper.create_embed(
            title=f"👋 {title}",
            description=description,
            color=COLORS["welcome"],
            thumbnail=thumbnail,
            image=image_url
        )
    
    @staticmethod
    def roast_embed(title: str, description: str = None) -> discord.Embed:
        """Create a roast-themed embed."""
        return EmbedHelper.create_embed(
            title=f"🔥 {title}",
            description=description,
            color=COLORS["roast"]
        )

class TimeHelper:
    """Helper class for time-related operations."""
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h"
    
    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """Format timestamp to readable string."""
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_discord_timestamp(timestamp: datetime, format_type: str = "R") -> str:
        """Get Discord timestamp format."""
        return f"<t:{int(timestamp.timestamp())}:{format_type}>"
    
    @staticmethod
    def parse_birthday(birthday_str: str) -> Optional[str]:
        """Parse birthday string to MM-DD format."""
        try:
            # Remove any separators and parse
            clean_date = birthday_str.replace('/', '-').replace('.', '-')
            parts = clean_date.split('-')
            
            if len(parts) == 2:
                month = int(parts[0])
                day = int(parts[1])
                
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return f"{month:02d}-{day:02d}"
            elif len(parts) == 3:
                # If year is included, ignore it
                month = int(parts[0])
                day = int(parts[1])
                
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return f"{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            pass
        
        return None
    
    @staticmethod
    def get_next_birthday_days(birthday_mm_dd: str) -> int:
        """Get days until next birthday."""
        today = datetime.now()
        current_year = today.year
        
        # Parse birthday
        month, day = map(int, birthday_mm_dd.split('-'))
        next_birthday = datetime(current_year, month, day)
        
        # If birthday has passed this year, use next year
        if next_birthday < today:
            next_birthday = datetime(current_year + 1, month, day)
        
        return (next_birthday - today).days
    
    @staticmethod
    def is_today(birthday_mm_dd: str) -> bool:
        """Check if birthday is today."""
        today = datetime.now()
        month, day = map(int, birthday_mm_dd.split('-'))
        return today.month == month and today.day == day

class PermissionHelper:
    """Helper class for permission checks."""
    
    @staticmethod
    def is_owner(user: Union[discord.User, discord.Member]) -> bool:
        """Check if user is bot owner."""
        return user.id in settings.OWNER_IDS
    
    @staticmethod
    def is_admin(member: discord.Member) -> bool:
        """Check if member has admin permissions."""
        return PermissionHelper.is_owner(member) or \
               member.guild_permissions.administrator or \
               member.guild_permissions.manage_guild
    
    @staticmethod
    def is_moderator(member: discord.Member) -> bool:
        """Check if member has moderator permissions."""
        return PermissionHelper.is_admin(member) or \
               member.guild_permissions.manage_messages or \
               member.guild_permissions.kick_members
    
    @staticmethod
    def can_manage_server(member: discord.Member) -> bool:
        """Check if member can manage server."""
        return PermissionHelper.is_admin(member)
    
    @staticmethod
    def get_permission_level(member: discord.Member) -> int:
        """Get permission level for member."""
        from config.constants import PERMISSION_LEVELS
        
        if PermissionHelper.is_owner(member):
            return PERMISSION_LEVELS["OWNER"]
        elif PermissionHelper.is_admin(member):
            return PERMISSION_LEVELS["ADMIN"]
        elif PermissionHelper.is_moderator(member):
            return PERMISSION_LEVELS["MODERATOR"]
        else:
            return PERMISSION_LEVELS["MEMBER"]

class XPHelper:
    """Helper class for XP-related operations."""
    
    @staticmethod
    def calculate_xp_for_next_level(current_level: int) -> int:
        """Calculate XP needed for next level."""
        from config.constants import XP_TABLE
        
        # Find the next level in the XP table
        levels = sorted(XP_TABLE.keys())
        current_index = levels.index(current_level) if current_level in levels else -1
        
        if current_index + 1 < len(levels):
            next_level = levels[current_index + 1]
            return XP_TABLE[next_level] - XP_TABLE.get(current_level, 0)
        
        return 1000  # Default for levels beyond table
    
    @staticmethod
    def get_xp_progress_bar(current_xp: int, total_needed: int, bar_length: int = 20) -> str:
        """Create a visual XP progress bar."""
        if total_needed == 0:
            return "█" * bar_length
        
        filled = int((current_xp / total_needed) * bar_length)
        empty = bar_length - filled
        
        bar = "█" * filled + "░" * empty
        percentage = int((current_xp / total_needed) * 100)
        
        return f"{bar} {percentage}%"
    
    @staticmethod
    async def assign_level_role(member: discord.Member, new_level: int) -> Optional[discord.Role]:
        """Assign level role to member."""
        guild = member.guild
        
        # Get the role for this level
        role_name_or_id = LEVEL_ROLE_MAP.get(new_level)
        if not role_name_or_id:
            return None
        
        # Find the role
        target_role = None
        if isinstance(role_name_or_id, int):
            target_role = guild.get_role(role_name_or_id)
        else:
            target_role = discord.utils.get(guild.roles, name=role_name_or_id)
        
        if not target_role:
            return None
        
        # Remove previous level roles
        roles_to_remove = []
        for level, role in LEVEL_ROLE_MAP.items():
            if role and level != new_level:
                if isinstance(role, int):
                    prev_role = guild.get_role(role)
                else:
                    prev_role = discord.utils.get(guild.roles, name=role)
                
                if prev_role and prev_role in member.roles:
                    roles_to_remove.append(prev_role)
        
        # Remove old roles and assign new one
        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason="Level up role update")
        
        await member.add_roles(target_role, reason="Level up achievement")
        return target_role

class SystemHelper:
    """Helper class for system operations."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_usage,
                "memory_used_mb": round(memory_used_mb, 2),
                "disk_percent": disk_usage,
                "disk_free_gb": round(disk_free_gb, 2),
                "process_count": len(psutil.pids())
            }
        except Exception:
            return {}
    
    @staticmethod
    def get_file_size(file_path: str) -> str:
        """Get human-readable file size."""
        try:
            size_bytes = os.path.getsize(file_path)
            
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        except OSError:
            return "Unknown"
    
    @staticmethod
    async def safe_send_message(channel, content: str = None,
                               embed: discord.Embed = None, ephemeral: bool = False) -> bool:
        """Safely send a message with error handling."""
        try:
            if isinstance(channel, discord.Interaction):
                if channel.response.is_done():
                    await channel.followup.send(content=content, embed=embed, ephemeral=ephemeral)
                else:
                    await channel.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
            else:
                await channel.send(content=content, embed=embed)
            return True
        except (discord.Forbidden, discord.HTTPException) as e:
            # Avoid circular import
            import logging
            logging.getLogger('bot').error(f"Failed to send message: {e}")
            return False
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input."""
        if not text:
            return ""
        
        # Remove potentially harmful characters
        sanitized = text.replace('@', '@\u200b')  # Zero-width space to prevent pings
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized.strip()
    
    @staticmethod
    def create_user_mention_safe(user_id: int) -> str:
        """Create safe user mention."""
        return f"<@{user_id}>"

class CooldownHelper:
    """Helper class for managing command cooldowns."""
    
    def __init__(self):
        self.cooldowns = {}
    
    def check_cooldown(self, user_id: int, command_name: str, cooldown_seconds: int) -> bool:
        """Check if user is on cooldown for command."""
        key = f"{user_id}:{command_name}"
        
        if key not in self.cooldowns:
            return True
        
        last_used = self.cooldowns[key]
        return (datetime.now() - last_used).total_seconds() >= cooldown_seconds
    
    def set_cooldown(self, user_id: int, command_name: str):
        """Set cooldown for user and command."""
        key = f"{user_id}:{command_name}"
        self.cooldowns[key] = datetime.now()
    
    def get_remaining_cooldown(self, user_id: int, command_name: str, cooldown_seconds: int) -> int:
        """Get remaining cooldown seconds."""
        key = f"{user_id}:{command_name}"
        
        if key not in self.cooldowns:
            return 0
        
        last_used = self.cooldowns[key]
        elapsed = (datetime.now() - last_used).total_seconds()
        remaining = cooldown_seconds - elapsed
        
        return max(0, int(remaining))

# Global instances
embed_helper = EmbedHelper()
time_helper = TimeHelper()
permission_helper = PermissionHelper()
xp_helper = XPHelper()
system_helper = SystemHelper()
cooldown_helper = CooldownHelper()

# Convenience functions
def create_embed(*args, **kwargs) -> discord.Embed:
    return embed_helper.create_embed(*args, **kwargs)

def format_duration(seconds: int) -> str:
    return time_helper.format_duration(seconds)

def is_owner(user: discord.User) -> bool:
    return permission_helper.is_owner(user)

def is_admin(member: discord.Member) -> bool:
    return permission_helper.is_admin(member)

def get_system_info() -> Dict[str, Any]:
    return system_helper.get_system_info()

async def safe_send_message(channel, content=None, embed=None, ephemeral=False):
    """Convenience function for safe message sending."""
    return await system_helper.safe_send_message(channel, content, embed, ephemeral)