"""
Helper functions for MalaBoT.
"""

import discord
import psutil
from datetime import datetime, timezone
import aiosqlite

from config.constants import MOD_ROLE_ID, OWNER_ID

# --- Embed Helper ---

def create_embed(title: str, description: str, color: discord.Color) -> discord.Embed:
    """Creates a discord.Embed object with a consistent style."""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="MalaBoT", icon_url="https://i.imgur.com/v2Jd8b3.png") # Replace with your bot's icon URL
    embed.timestamp = datetime.now(timezone.utc)
    return embed

# --- Permission Checkers ---

async def is_owner(interaction: discord.Interaction) -> bool:
    """Check if the user is the bot owner."""
    is_owner_check = interaction.user.id == OWNER_ID
    if not is_owner_check:
        await interaction.response.send_message(
            embed=create_embed("Permission Denied", "You do not have permission to use this command.", discord.Color.red()),
            ephemeral=True
        )
    return is_owner_check

async def check_mod_permission(interaction: discord.Interaction, db_manager) -> bool:
    """
    Checks if a user has moderator permissions.
    A user is considered a mod if they have the 'mod_role' from settings,
    have administrator permissions, or are the guild owner.
    """
    if interaction.user.guild_permissions.administrator or interaction.user.id == interaction.guild.owner_id:
        return True

    mod_role_id = await db_manager.get_setting("mod_role", interaction.guild.id)
    if mod_role_id and discord.utils.get(interaction.user.roles, id=int(mod_role_id)):
        return True

    await interaction.response.send_message(
        embed=create_embed("Permission Denied", "You need to be a moderator to use this command.", discord.Color.red()),
        ephemeral=True
    )
    return False

# --- Safe Messaging ---

async def safe_send_message(interaction: discord.Interaction, content: str = None, embed: discord.Embed = None, ephemeral: bool = True):
    """Safely sends a message to an interaction, handling cases where the interaction might be deferred."""
    try:
        if interaction.response.is_done():
            await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
    except discord.errors.InteractionResponded:
        await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
    except Exception as e:
        print(f"Failed to send message: {e}")


# --- System Info ---

def get_system_info():
    """Returns a dictionary with system resource usage."""
    process = psutil.Process()
    with process.oneshot():
        cpu_percent = psutil.cpu_percent(interval=1)
        mem_info = psutil.virtual_memory()
        mem_percent = mem_info.percent
        disk_info = psutil.disk_usage('/')
        disk_percent = disk_info.percent
        
        return {
            "cpu": f"{cpu_percent:.2f}%",
            "memory": f"{mem_percent:.2f}%",
            "disk": f"{disk_percent:.2f}%"
        }