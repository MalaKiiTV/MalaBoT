"""
XP and leveling system cog for MalaBoT.
Handles user XP gains, level progression, and XP administration.
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import datetime
from typing import Optional

from utils.logger import get_logger
from utils.helpers import (
    embed_helper, xp_helper, time_helper, cooldown_helper,
    create_embed, is_owner, permission_helper
)
from config.constants import COLORS, XP_TABLE, XP_PER_MESSAGE, XP_PER_REACTION, XP_PER_VOICE_MINUTE, XP_COOLDOWN_SECONDS, DAILY_CHECKIN_XP, STREAK_BONUS_PERCENT
from config.settings import settings



class XPGroup(app_commands.Group):
    """XP command group"""
    def __init__(self, cog):
        super().__init__(name="xp", description="XP and leveling system commands")
        self.cog = cog
    
    @app_commands.command(name="rank", description="Check your or another user's rank and XP")
    @app_commands.describe(user="User to check (leave empty for yourself)")
    async def rank(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Check XP rank."""
        try:
            target = user or interaction.user
            
            # Get user stats
            xp = await self.cog.bot.db_manager.get_user_xp(target.id)
            level = await self.cog.bot.db_manager.get_user_level(target.id)
            
            # Get rank
            conn = await self.cog.bot.db_manager.get_connection()
            cursor = await conn.execute(
                "SELECT COUNT(*) + 1 FROM users WHERE xp > ?",
                (xp,)
            )
            rank = (await cursor.fetchone())[0]
            
            # Calculate XP for next level
            next_level_xp = xp_helper.xp_for_level(level + 1)
            current_level_xp = xp_helper.xp_for_level(level)
            xp_needed = next_level_xp - xp
            xp_progress = xp - current_level_xp
            xp_total_needed = next_level_xp - current_level_xp
            
            # Create progress bar
            progress = int((xp_progress / xp_total_needed) * 20)
            progress_bar = "█" * progress + "░" * (20 - progress)
            
            embed = create_embed(
                title=f"📊 {target.display_name}'s Rank",
                description=f"**Rank:** #{rank}\n**Level:** {level}\n**XP:** {xp:,} / {next_level_xp:,}\n\n{progress_bar}\n\n**XP Needed:** {xp_needed:,}",
                color=COLORS['primary']
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp rank command: {e}")
            await self.cog._error_response(interaction, "Failed to get rank")
    
    @app_commands.command(name="leaderboard", description="Show server XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Show XP leaderboard."""
        try:
            await interaction.response.defer()
            
            # Get top 10 users
            conn = await self.cog.bot.db_manager.get_connection()
            cursor = await conn.execute(
                "SELECT user_id, xp FROM users WHERE xp > 0 ORDER BY xp DESC LIMIT 10"
            )
            top_users = await cursor.fetchall()
            
            if not top_users:
                embed = embed_helper.warning_embed(
                    title="📊 XP Leaderboard",
                    description="No users have earned XP yet!"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Build leaderboard
            description = ""
            for i, (user_id, xp) in enumerate(top_users, 1):
                user = interaction.guild.get_member(user_id)
                if user:
                    level = await self.cog.bot.db_manager.get_user_level(user_id)
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"**{i}.**"
                    description += f"{medal} {user.mention} - Level {level} ({xp:,} XP)\n"
            
            embed = create_embed(
                title="📊 XP Leaderboard",
                description=description,
                color=COLORS['primary']
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp leaderboard command: {e}")
            await self.cog._error_response(interaction, "Failed to get leaderboard")
    
    @app_commands.command(name="checkin", description="Claim your daily XP bonus")
    async def checkin(self, interaction: discord.Interaction):
        """Daily XP check-in."""
        try:
            user_id = interaction.user.id
            
            # Check if user already claimed today
            last_daily = await self.cog.bot.db_manager.get_user_last_daily(user_id)
            now = datetime.datetime.now()
            
            if last_daily:
                last_daily_date = datetime.datetime.fromisoformat(last_daily)
                if last_daily_date.date() == now.date():
                    # Already claimed today
                    next_daily = last_daily_date + datetime.timedelta(days=1)
                    time_until = next_daily - now
                    hours = int(time_until.total_seconds() // 3600)
                    minutes = int((time_until.total_seconds() % 3600) // 60)
                    
                    embed = embed_helper.warning_embed(
                        title="⏰ Already Claimed",
                        description=f"You've already claimed your daily XP!\n\nNext check-in available in: **{hours}h {minutes}m**"
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            # Award daily XP
            xp_amount = DAILY_CHECKIN_XP
            await self.cog.bot.db_manager.update_user_xp(user_id, xp_amount)
            await self.cog.bot.db_manager.update_user_last_daily(user_id, now.isoformat())
            
            # Check for streak bonus
            streak = await self.cog.bot.db_manager.get_user_streak(user_id)
            if last_daily:
                last_daily_date = datetime.datetime.fromisoformat(last_daily)
                if (now.date() - last_daily_date.date()).days == 1:
                    # Consecutive day, increase streak
                    streak += 1
                    await self.cog.bot.db_manager.update_user_streak(user_id, streak)
                else:
                    # Streak broken
                    streak = 1
                    await self.cog.bot.db_manager.update_user_streak(user_id, 1)
            else:
                # First daily
                streak = 1
                await self.cog.bot.db_manager.update_user_streak(user_id, 1)
            
            # Calculate streak bonus
            if streak > 1:
                bonus_xp = int(xp_amount * (STREAK_BONUS_PERCENT / 100) * min(streak, 7))
                await self.cog.bot.db_manager.update_user_xp(user_id, bonus_xp)
                total_xp = xp_amount + bonus_xp
                
                embed = embed_helper.success_embed(
                    title="✅ Daily Check-in",
                    description=f"You claimed **{xp_amount} XP**!\n\n🔥 **{streak} Day Streak!**\nBonus: **+{bonus_xp} XP**\n\n**Total: {total_xp} XP**"
                )
            else:
                embed = embed_helper.success_embed(
                    title="✅ Daily Check-in",
                    description=f"You claimed **{xp_amount} XP**!\n\nCome back tomorrow to start a streak! 🔥"
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp checkin command: {e}")
            await self.cog._error_response(interaction, "Failed to claim daily XP")
    
    # ==================== ADMIN COMMANDS ====================
    
    @app_commands.command(name="add", description="Add XP to a user (Server Owner only)")
    @app_commands.describe(
        user="User to add XP to",
        amount="Amount of XP to add"
    )
    async def add(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Add XP to a user."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if amount <= 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount must be greater than 0."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await self.cog.bot.db_manager.update_user_xp(user.id, amount)
            
            embed = embed_helper.success_embed(
                title="✅ XP Added",
                description=f"Added {amount:,} XP to {user.mention}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.cog.logger.info(f"Admin {interaction.user.name} added {amount} XP to {user.name}")
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp add command: {e}")
            await self.cog._error_response(interaction, "Failed to add XP")
    
    @app_commands.command(name="add-all", description="Add XP to ALL users in the server (Server Owner only)")
    @app_commands.describe(
        amount="Amount of XP to add to each user",
        confirm="Type 'yes' to confirm adding XP to ALL users"
    )
    async def add_all(self, interaction: discord.Interaction, amount: int, confirm: str):
        """Add XP to all users."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if confirm != "yes":
                embed = embed_helper.warning_embed(
                    title="⚠️ Confirmation Required",
                    description=f"This will add **{amount:,} XP** to **ALL users** in the server!\n\nUse: `/xp add-all amount:{amount} confirm:yes`"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if amount <= 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount must be greater than 0."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            
            # Add XP to all members
            added_count = 0
            for member in interaction.guild.members:
                if not member.bot:
                    await self.cog.bot.db_manager.update_user_xp(member.id, amount)
                    added_count += 1
            
            embed = embed_helper.success_embed(
                title="✅ XP Added to All Users",
                description=f"Added **{amount:,} XP** to **{added_count}** users"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            self.cog.logger.info(f"Admin {interaction.user.name} added {amount} XP to all users ({added_count} users)")
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp add-all command: {e}")
            await self.cog._error_response(interaction, "Failed to add XP to all users")
    
    @app_commands.command(name="remove", description="Remove XP from a user (Server Owner only)")
    @app_commands.describe(
        user="User to remove XP from",
        amount="Amount of XP to remove"
    )
    async def remove(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Remove XP from a user."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if amount <= 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount must be greater than 0."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            current_xp = await self.cog.bot.db_manager.get_user_xp(user.id)
            new_xp = max(0, current_xp - amount)
            
            await self.cog.bot.db_manager.set_user_xp(user.id, new_xp)
            
            embed = embed_helper.success_embed(
                title="✅ XP Removed",
                description=f"Removed {amount:,} XP from {user.mention}\n\nNew XP: {new_xp:,}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.cog.logger.info(f"Admin {interaction.user.name} removed {amount} XP from {user.name}")
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp remove command: {e}")
            await self.cog._error_response(interaction, "Failed to remove XP")
    
    @app_commands.command(name="set", description="Set user XP to a specific amount (Server Owner only)")
    @app_commands.describe(
        user="User to set XP for",
        amount="Amount of XP to set"
    )
    async def set(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Set user XP."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if amount < 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount cannot be negative."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await self.cog.bot.db_manager.set_user_xp(user.id, amount)
            
            embed = embed_helper.success_embed(
                title="✅ XP Set",
                description=f"Set {user.mention}'s XP to {amount:,}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.cog.logger.info(f"Admin {interaction.user.name} set {user.name}'s XP to {amount}")
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp set command: {e}")
            await self.cog._error_response(interaction, "Failed to set XP")
    
    @app_commands.command(name="reset", description="Reset a user's XP to 0 (Server Owner only)")
    @app_commands.describe(user="User to reset XP for")
    async def reset(self, interaction: discord.Interaction, user: discord.Member):
        """Reset user XP."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await self.cog.bot.db_manager.reset_user_xp(user.id)
            
            embed = embed_helper.success_embed(
                title="✅ XP Reset",
                description=f"Reset {user.mention}'s XP and level to 0"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.cog.logger.info(f"Admin {interaction.user.name} reset {user.name}'s XP")
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp reset command: {e}")
            await self.cog._error_response(interaction, "Failed to reset XP")
    
    @app_commands.command(name="reset-all", description="Reset ALL users' XP to 0 (Server Owner only)")
    @app_commands.describe(confirm="Type 'yes' to confirm resetting ALL users")
    async def reset_all(self, interaction: discord.Interaction, confirm: str):
        """Reset all users' XP."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if confirm != "yes":
                embed = embed_helper.warning_embed(
                    title="⚠️ Confirmation Required",
                    description="This will reset **ALL users'** XP!\n\n`/xp reset-all confirm:yes`"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            conn = await self.cog.bot.db_manager.get_connection()
            cursor = await conn.execute("SELECT user_id FROM users WHERE xp > 0")
            users = await cursor.fetchall()
            
            reset_count = 0
            for user_row in users:
                await self.cog.bot.db_manager.reset_user_xp(user_row[0])
                reset_count += 1
            
            embed = embed_helper.success_embed(
                title="✅ All XP Reset",
                description=f"Reset {reset_count} users"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            self.cog.logger.info(f"Admin {interaction.user.name} reset all users' XP")
            
        except Exception as e:
            self.cog.logger.error(f"Error in xp reset-all command: {e}")
            await self.cog._error_response(interaction, "Failed to reset all XP")
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="❌ Error",
            description=message
        )
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    xp_cog = XP(bot)
    await bot.add_cog(xp_cog)

class XP(commands.Cog):
    """XP and leveling system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('xp')
        self.last_xp_time = {}  # Track last XP gain time per user
    

    async def cog_unload(self):
        """Remove the command group when cog is unloaded"""
        self.bot.tree.remove_command(self.xp_group.name)
    @commands.Cog.listener()
    async def on_message(self, message):
        """Award XP for messages."""
        try:
            # Ignore bots and DMs
            if message.author.bot or not message.guild:
                return
            
            guild_id = message.guild.id
            user_id = message.author.id
            current_time = datetime.datetime.now().timestamp()
            
            # Get guild-specific XP settings
            xp_per_message = await self.bot.db_manager.get_setting(f"xp_per_message_{guild_id}")
            xp_cooldown = await self.bot.db_manager.get_setting(f"xp_cooldown_{guild_id}")
            
            # Use defaults if not configured
            if not xp_per_message:
                xp_per_message = str(XP_PER_MESSAGE)  # Default to 10
            if not xp_cooldown:
                xp_cooldown = str(XP_COOLDOWN_SECONDS)  # Default to 60
            
            xp_amount = int(xp_per_message)
            cooldown = int(xp_cooldown)
            
            # Check cooldown
            key = f"{guild_id}_{user_id}"
            if key in self.last_xp_time:
                time_since_last = current_time - self.last_xp_time[key]
                if time_since_last < cooldown:
                    return
            
            # Update last XP time
            self.last_xp_time[key] = current_time
            
            # Award XP
            await self._award_xp(message.author, xp_amount, message.channel)
            
        except Exception as e:
            self.logger.error(f"Error in on_message XP: {e}")
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Award XP when user's message receives a reaction."""
        try:
            # Ignore bots and self-reactions
            if user.bot or reaction.message.author.bot:
                return
            
            # Don't award XP for reacting to your own message
            if user.id == reaction.message.author.id:
                return
            
            guild_id = reaction.message.guild.id
            
            # Get guild-specific reaction XP setting
            xp_per_reaction = await self.bot.db_manager.get_setting(f"xp_per_reaction_{guild_id}")
            
            # Use default if not configured
            if not xp_per_reaction:
                xp_per_reaction = str(XP_PER_REACTION)  # Default to 2
            
            xp_amount = int(xp_per_reaction)
            
            # Award XP to the message author (not the reactor)
            await self._award_xp(reaction.message.author, xp_amount, reaction.message.channel)
            
        except Exception as e:
            self.logger.error(f"Error in on_reaction_add XP: {e}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Award XP for voice chat participation."""
        try:
            # Ignore bots
            if member.bot:
                return
            
            guild_id = member.guild.id
            
            # Get guild-specific voice XP setting
            xp_per_voice = await self.bot.db_manager.get_setting(f"xp_per_voice_{guild_id}")
            
            # Use default if not configured
            if not xp_per_voice:
                xp_per_voice = str(XP_PER_VOICE_MINUTE)  # Default to 5
            
            xp_amount = int(xp_per_voice)
            
            # Award XP when user leaves voice channel
            if before.channel and not after.channel:
                await self._award_xp(member, xp_amount, None)
            
        except Exception as e:
            self.logger.error(f"Error in on_voice_state_update XP: {e}")
    
    async def _award_xp(self, user: discord.Member, amount: int, channel: Optional[discord.TextChannel] = None):
        """Award XP to a user and check for level up."""
        try:
            old_level = await self.bot.db_manager.get_user_level(user.id)
            await self.bot.db_manager.update_user_xp(user.id, amount)
            new_level = await self.bot.db_manager.get_user_level(user.id)
            
            # Check for level up
            if new_level > old_level and channel:
                await self._handle_level_up(user, new_level, channel)
                
        except Exception as e:
            self.logger.error(f"Error awarding XP: {e}")
    
    async def _handle_level_up(self, user: discord.Member, new_level: int, channel: discord.TextChannel):
        """Handle level up event."""
        try:
            guild_id = user.guild.id
            
            # Get custom level-up message
            level_up_message = await self.bot.db_manager.get_setting(f"level_up_message_{guild_id}")
            level_up_channel_id = await self.bot.db_manager.get_setting(f"level_up_channel_{guild_id}")
            
            # Use custom channel if configured
            if level_up_channel_id:
                level_up_channel = user.guild.get_channel(int(level_up_channel_id))
                if level_up_channel:
                    channel = level_up_channel
            
            # Format message with variables
            if level_up_message:
                message = level_up_message.replace("{user}", user.mention)
                message = message.replace("{level}", str(new_level))
            else:
                message = f"🎉 {user.mention} leveled up to **Level {new_level}**!"
            
            embed = embed_helper.success_embed(
                title="🎉 Level Up!",
                description=message
            )
            
            await channel.send(embed=embed)
            
            # Check for level role rewards
            await self._check_level_roles(user, new_level)
            
        except Exception as e:
            self.logger.error(f"Error handling level up: {e}")
    
    async def _check_level_roles(self, user: discord.Member, level: int):
        """Check and assign level role rewards."""
        try:
            guild_id = user.guild.id
            level_roles = await self.bot.db_manager.get_setting(f"level_roles_{guild_id}")
            
            if not level_roles:
                return
            
            # Parse level roles (format: "level:role_id,level:role_id")
            for role_entry in level_roles.split(","):
                if ":" not in role_entry:
                    continue
                
                role_level, role_id = role_entry.split(":")
                role_level = int(role_level)
                
                # If user reached this level, assign the role
                if level >= role_level:
                    role = user.guild.get_role(int(role_id))
                    if role and role not in user.roles:
                        await user.add_roles(role, reason=f"Reached level {role_level}")
                        self.logger.info(f"Assigned role {role.name} to {user.name} for reaching level {role_level}")
                        
        except Exception as e:
            self.logger.error(f"Error checking level roles: {e}")


