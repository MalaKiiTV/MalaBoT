"""
Helper utilities for MalaBoT
Provides various helper classes and functions for common operations
"""

import discord
from datetime import datetime, timedelta
from typing import Dict, Any
import psutil
import os
import platform
import random

from config.constants import COLORS
from utils.logger import get_logger

logger = get_logger(__name__)

def log_moderation(message: str):
    """Log moderation actions."""
    logger.info(message)

def log_xp(message: str):
    """Log XP-related actions."""
    logger.info(message)

def log_birthday(message: str):
    """Log birthday-related actions."""
    logger.info(message)

class EmbedHelper:
    """Helper class for creating consistent embeds."""
    
    @staticmethod
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
        
        return embed
    
    @staticmethod
    def error_embed(title: str, description: str) -> discord.Embed:
        """Create an error embed with red color."""
        return EmbedHelper.create_embed(title, description, COLORS['error'])
    
    @staticmethod
    def success_embed(title: str, description: str) -> discord.Embed:
        """Create a success embed with green color."""
        return EmbedHelper.create_embed(title, description, COLORS['success'])
    
    @staticmethod
    def info_embed(title: str, description: str) -> discord.Embed:
        """Create an info embed with blue color."""
        return EmbedHelper.create_embed(title, description, COLORS['info'])

    @staticmethod
    def roast_embed(title: str, description: str) -> discord.Embed:
        """Create a roast embed with orange color."""
        return EmbedHelper.create_embed(title, description, COLORS['warning'])


class TimeHelper:
    """Helper class for time-related operations."""
    
    @staticmethod
    def format_duration(td) -> str:
        """Format duration (timedelta or seconds) to human-readable string."""
        # If it's a timedelta object, convert to seconds
        if isinstance(td, datetime):
            # If a datetime object is passed, calculate difference from now
            td = datetime.now() - td
        if hasattr(td, 'total_seconds'):
            seconds = int(td.total_seconds())
        else:
            # If already an integer/float, use as seconds
            seconds = int(td)
            
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
            minutes = (seconds % 3600) // 60
            return f"{days}d {hours}h {minutes}m"


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

class PermissionHelper:
    """Helper class for permission-related operations."""
    
    @staticmethod
    def is_owner(user: discord.User) -> bool:
        """Check if user is a bot owner."""
        from config.settings import settings
        return str(user.id) in settings.OWNER_IDS

    @staticmethod
    def is_admin(member: discord.Member) -> bool:
        """Check if member has administrator permissions."""
        return member.guild_permissions.administrator

class XPHelper:
    """Helper class for XP-related operations."""
    
    @staticmethod
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
        return level
    
    @staticmethod
    def get_xp_for_next_level(current_level: int, xp_table: Dict[int, int]) -> int:
        """Get XP required for next level."""
        next_level = current_level + 1
        return xp_table.get(next_level, xp_table[max(xp_table.keys())])
    
    @staticmethod
    def get_xp_for_level(level: int, xp_table: Dict[int, int] = None) -> int:
        """Get XP required for a specific level."""
        if xp_table is None:
            from config.constants import XP_TABLE
            xp_table = XP_TABLE
        return xp_table.get(level, 0)
    
    @staticmethod
    def get_random_xp(min_xp: int, max_xp: int) -> int:
        """Get random XP amount within range."""
        return random.randint(min_xp, max_xp)

class RoleHelper:
    """Helper class for role-related operations."""
    
    @staticmethod
    async def add_role_to_member(member: discord.Member, role_name_or_id) -> bool:
        """Add a role to a member by name or ID."""
        try:
            if not role_name_or_id:
                return False
                
            # Try to find role by ID first, then by name
            role = None
            if isinstance(role_name_or_id, int) or role_name_or_id.isdigit():
                role = discord.utils.get(member.guild.roles, id=int(role_name_or_id))
            else:
                role = discord.utils.get(member.guild.roles, name=role_name_or_id)
                
            if not role:
                return False
                
            await member.add_roles(role)
            return True
        except:
            return False

class CooldownHelper:
    """Helper class for cooldown management."""
    
    def __init__(self):
        self.cooldowns = {}
    
    def is_on_cooldown(self, user_id: int, command: str) -> bool:
        """Check if user is on cooldown for a command."""
        key = f"{user_id}_{command}"
        if key in self.cooldowns:
            return datetime.now() < self.cooldowns[key]
        return False
    
    def set_cooldown(self, user_id: int, command: str, seconds: int = None):
        """Set a cooldown for a user on a command."""
        if seconds is None:
            # Import here to avoid circular dependency
            from config.constants import COMMAND_COOLDOWNS
            seconds = COMMAND_COOLDOWNS.get(command, 5)
        
        key = f"{user_id}_{command}"
        self.cooldowns[key] = datetime.now() + timedelta(seconds=seconds)
    
    def get_remaining_cooldown(self, user_id: int, command: str) -> int:
        """Get remaining cooldown time in seconds."""
        key = f"{user_id}_{command}"
        if key in self.cooldowns:
            remaining = (self.cooldowns[key] - datetime.now()).total_seconds()
            return max(0, int(remaining))
        return 0
    
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

    
class SystemHelper:
    """Helper class for system-related operations."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get system information."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'platform_release': platform.release(),
            'cpu_count': psutil.cpu_count(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': memory_info.rss / 1024 / 1024,  # MB
            'memory_percent': process.memory_percent(),
            'disk_usage': psutil.disk_usage('/'),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def get_file_size(file_path: str) -> str:
        """Get file size in human-readable format."""
        try:
            size_bytes = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} TB"
        except:
            return "Unknown"
    
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

# Convenience instances
embed_helper = EmbedHelper()
time_helper = TimeHelper()
permission_helper = PermissionHelper()
xp_helper = XPHelper()
cooldown_helper = CooldownHelper()
system_helper = SystemHelper()

# Convenience functions
def create_embed(*args, **kwargs) -> discord.Embed:
    return embed_helper.create_embed(*args, **kwargs)

def format_duration(seconds) -> str:
    return time_helper.format_duration(seconds)

def is_owner(user: discord.User) -> bool:
    return permission_helper.is_owner(user)

def is_admin(member: discord.Member) -> bool:
    return permission_helper.is_admin(member)

def get_system_info() -> Dict[str, Any]:
    return system_helper.get_system_info()

async def is_mod(interaction: discord.Interaction, db_manager, specific_mod_role_key: str = None) -> bool:
    """
    Check if user has mod permissions.
    
    Args:
        interaction: The Discord interaction
        db_manager: Database manager instance
        specific_mod_role_key: Optional specific mod role key (e.g., 'verification_mod_role')
                               If provided, checks this role first, then falls back to general mod role
    
    Returns:
        bool: True if user is owner or has mod role
    """
    # Owner always has access
    if is_owner(interaction.user):
        return True
    
    guild_id = interaction.guild_id
    if not guild_id:
        return False
    
    # Check specific mod role first if provided
    if specific_mod_role_key:
        specific_role_id = await db_manager.get_setting(f"{specific_mod_role_key}_{guild_id}")
        if specific_role_id:
            specific_role = interaction.guild.get_role(int(specific_role_id))
            if specific_role and specific_role in interaction.user.roles:
                return True
    
    # Fall back to general mod role
    mod_role_id = await db_manager.get_setting(f"mod_role_{guild_id}")
    if not mod_role_id:
        return False
    
    mod_role = interaction.guild.get_role(int(mod_role_id))
    if not mod_role:
        return False
    
    return mod_role in interaction.user.roles

async def check_mod_permission(interaction: discord.Interaction, db_manager, specific_mod_role_key: str = None) -> bool:
    """
    Check mod permission and send error message if denied.
    
    Args:
        interaction: The Discord interaction
        db_manager: Database manager instance
        specific_mod_role_key: Optional specific mod role key
    
    Returns:
        bool: True if user has permission, False otherwise (and sends error message)
    """
    if await is_mod(interaction, db_manager, specific_mod_role_key):
        return True
    
    # Get role names for error message
    role_names = []
    guild_id = interaction.guild_id
    
    if specific_mod_role_key:
        specific_role_id = await db_manager.get_setting(f"{specific_mod_role_key}_{guild_id}")
        if specific_role_id:
            specific_role = interaction.guild.get_role(int(specific_role_id))
            if specific_role:
                role_names.append(specific_role.name)
    
    mod_role_id = await db_manager.get_setting(f"mod_role_{guild_id}")
    if mod_role_id:
        mod_role = interaction.guild.get_role(int(mod_role_id))
        if mod_role:
            role_names.append(mod_role.name)
    
    role_list = "\n".join([f"• {name}" for name in role_names]) if role_names else "• No mod role configured"
    
    embed = embed_helper.error_embed(
        title="🚫 Permission Denied",
        description=f"This command is only available to:\n\n"
                   f"• Bot Owners\n"
                   f"• Users with mod role:\n{role_list}\n\n"
                   f"Your current permissions:\n"
                   f"• Bot Owner: {'✅' if is_owner(interaction.user) else '❌'}"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
    return False

async def safe_send_message(channel, content=None, embed=None, ephemeral=False, **kwargs):
    """Safely send a message to a channel with error handling."""
    try:
        if hasattr(channel, 'send'):  # Regular channel
            return await channel.send(content=content, embed=embed, **kwargs)
        elif hasattr(channel, 'followup'):  # Interaction followup
            return await channel.followup.send(content=content, embed=embed, ephemeral=ephemeral, **kwargs)
        else:  # Assume it's an interaction
            if ephemeral:
                return await channel.response.send_message(content=content, embed=embed, ephemeral=True, **kwargs)
            else:
                return await channel.response.send_message(content=content, embed=embed, **kwargs)
    except discord.Forbidden:
        # Bot doesn't have permission to send messages in this channel
        print(f"Missing permissions to send message in {channel}")
        return None
    except discord.HTTPException as e:
        # Other Discord API errors
        print(f"Failed to send message: {e}")
        return None
    except Exception as e:
        # Any other errors
        print(f"Unexpected error when sending message: {e}")
        return None
async def is_staff(interaction: discord.Interaction, db_manager) -> bool:
    """Check if user has staff permissions (alias for is_mod)."""
    return await is_mod(interaction, db_manager)

async def check_staff_permission(interaction: discord.Interaction, db_manager) -> bool:
    """Check staff permission and send error message if denied."""
    return await check_mod_permission(interaction, db_manager)
