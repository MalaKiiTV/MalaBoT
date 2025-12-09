"""Audit logging utilities"""

import discord
from datetime import datetime
from src.utils.logger import log_system


async def log_audit(bot, guild_id: int, user_id: int, action: str, details: str):
    """Log action to audit channel"""
    
    audit_channel_id = await bot.db_manager.get_setting("audit_channel", guild_id)
    
    if not audit_channel_id:
        return
    
    channel = bot.get_channel(int(audit_channel_id))
    if not channel:
        return
    
    guild = bot.get_guild(guild_id)
    user = guild.get_member(user_id) if guild else None
    user_mention = user.mention if user else f"User ID: {user_id}"
    
    action_emojis = {
        "appeal_submitted": "📝",
        "appeal_approved": "✅",
        "appeal_denied": "❌",
        "appeal_withdrawn": "↩️",
        "appeal_cancelled": "🚫"
    }
    
    action_colors = {
        "appeal_submitted": 0x0099ff,
        "appeal_approved": 0x00ff00,
        "appeal_denied": 0xff0000,
        "appeal_withdrawn": 0xffaa00,
        "appeal_cancelled": 0x808080
    }
    
    emoji = action_emojis.get(action, "📋")
    color = action_colors.get(action, 0x0099ff)
    
    embed = discord.Embed(
        title=f"{emoji} {action.replace('_', ' ').title()}",
        description=f"**User:** {user_mention}\n**Time:** <t:{int(datetime.now().timestamp())}:F>\n\n{details}",
        color=color,
        timestamp=datetime.now()
    )
    
    try:
        await channel.send(embed=embed)
        log_system(f"[AUDIT] {action} for user {user_id}")
    except Exception as e:
        log_system(f"[AUDIT] Failed: {e}", level="error")
