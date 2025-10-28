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
    create_embed, is_admin, is_owner, permission_helper
)
from config.constants import COLORS, XP_TABLE, XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX, XP_COOLDOWN_SECONDS, DAILY_CHECKIN_XP, STREAK_BONUS_PERCENT
from config.settings import settings

class XP(commands.Cog):
    """XP and leveling system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('xp')
        self.last_xp_time = {}  # Track last XP gain time per user
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Award XP for messages."""
        try:
            # Ignore bots and DMs
            if message.author.bot or not message.guild:
                return
            
            # Check cooldown
            user_id = message.author.id
            current_time = datetime.datetime.now().timestamp()
            
            if user_id in self.last_xp_time:
                time_diff = current_time - self.last_xp_time[user_id]
                if time_diff < XP_COOLDOWN_SECONDS:
                    return
            
            # Award XP
            xp_gained = random.randint(XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX)
            await self.bot.db_manager.update_user_xp(message.author.id, xp_gained)
            
            # Update last XP time
            self.last_xp_time[user_id] = current_time
            
            # Check for level up
            user_data = await self.bot.db_manager.get_user(message.author.id)
            if user_data:
                current_level = xp_helper.calculate_level_from_xp(user_data.get('xp', 0))
                if current_level > user_data.get('level', 0):
                    await self._handle_level_up(message.author, message.guild, current_level, user_data.get('level', 0))
            
        except Exception as e:
            self.logger.error(f"Error in on_message XP: {e}")
    
    async def _handle_level_up(self, member: discord.Member, guild: discord.Guild, new_level: int, old_level: int):
        """Handle user level up."""
        try:
            # Send level up message
            channel = member.guild.system_channel or member.guild.text_channels[0]
            
            embed = create_embed(
                title=f"🎉 Level Up!",
                description=f"{member.mention} has reached level **{new_level}**!",
                color=COLORS["success"]
            )
            
            await channel.send(embed=embed)
            
            # Update database
            await self.bot.db_manager.update_user_xp(member.id, 0)  # Update level in database
            
            # Assign level role if configured
            await xp_helper.assign_level_role(member, new_level)
            
            self.logger.info(f"{member.name} leveled up to {new_level} in {guild.name}")
            
        except Exception as e:
            self.logger.error(f"Error handling level up: {e}")
    
    @app_commands.command(name="rank", description="Check your or another user's rank and XP")
    @app_commands.describe(user="User to check (leave empty to check yourself)")
    async def rank(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Check user rank and XP."""
        try:
            target_user = user or interaction.user
            
            # Get user XP data
            user_data = await self.bot.db_manager.get_user(target_user.id)
            
            if not user_data or user_data.get('xp', 0) == 0:
                embed = embed_helper.error_embed(
                    title="No XP Data",
                    description=f"{target_user.mention} hasn't earned any XP yet."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Calculate rank info
            current_xp = user_data.get('xp', 0)
            current_level = xp_helper.calculate_level_from_xp(current_xp)
            level_xp = xp_helper.get_xp_for_level(current_level)
            next_level_xp = xp_helper.get_xp_for_level(current_level + 1)
            xp_to_next = next_level_xp - current_xp
            level_progress = current_xp - level_xp
            level_total = next_level_xp - level_xp
            progress_percent = (level_progress / level_total) * 100 if level_total > 0 else 0
            
            # Get server rank
            server_rank = await self.bot.db_manager.get_user_rank(target_user.id, interaction.guild.id)
            
            # Create embed
            embed = create_embed(
                title=f"📊 {target_user.display_name}'s Rank",
                color=COLORS["info"]
            )
            
            embed.set_thumbnail(url=target_user.display_avatar.url if target_user.display_avatar else target_user.default_avatar.url)
            
            embed.add_field(
                name="🏆 Rank",
                value=f"#{server_rank:,}" if server_rank else "#N/A",
                inline=True
            )
            
            embed.add_field(
                name="⭐ Level",
                value=f"{current_level}",
                inline=True
            )
            
            embed.add_field(
                name="💎 Total XP",
                value=f"{current_xp:,}",
                inline=True
            )
            
            # Progress bar
            progress_bar = "█" * int(progress_percent // 10) + "░" * (10 - int(progress_percent // 10))
            embed.add_field(
                name="📈 Progress to Level {current_level + 1}",
                value=f"{progress_bar} {progress_percent:.1f}%\n{level_progress:,} / {level_total:,} XP",
                inline=False
            )
            
            embed.add_field(
                name="🎯 XP to Next Level",
                value=f"{xp_to_next:,}",
                inline=True
            )
            
            # Check if daily is available
            from datetime import date
            today = date.today().isoformat()
            last_daily = user_data.get('last_daily_award_date')
            daily_available = last_daily != today
            
            embed.add_field(
                name="📅 Daily Check-in",
                value=f"✅ Available" if daily_available else "❌ Already claimed",
                inline=True
            )
            
            embed.set_footer(text=f"Requested by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in rank command: {e}")
            await self._error_response(interaction, "Failed to get rank information")
    
    @app_commands.command(name="leaderboard", description="Show server XP leaderboard")
    @app_commands.describe(limit="Number of users to show (max 25)")
    async def leaderboard(self, interaction: discord.Interaction, limit: int = 10):
        """Show XP leaderboard."""
        try:
            limit = min(max(1, limit), 25)  # Ensure between 1 and 25
            
            # Get leaderboard data
            leaderboard_data = await self.bot.db_manager.get_leaderboard(interaction.guild.id, limit)
            
            if not leaderboard_data:
                embed = embed_helper.error_embed(
                    title="No Leaderboard Data",
                    description="No XP data available for this server."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create embed
            embed = create_embed(
                title=f"🏆 {interaction.guild.name} XP Leaderboard",
                color=COLORS["info"]
            )
            
            # Format leaderboard entries
            leaderboard_text = ""
            for i, user_data in enumerate(leaderboard_data, 1):
                # Get user object
                try:
                    user = self.bot.get_user(user_data['user_id'])
                    if not user:
                        user = await self.bot.fetch_user(user_data['user_id'])
                except:
                    user = None
                
                if user:
                    # Determine medal
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    else:
                        medal = f"#{i}"
                    
                    leaderboard_text += f"{medal} **{user.display_name}** - Level {user_data.get('level', 0)} ({user_data.get('xp', 0):,} XP)\n"
                else:
                    leaderboard_text += f"#{i} Unknown User - Level {user_data.get('level', 0)} ({user_data.get('xp', 0):,} XP)\n"
            
            embed.description = leaderboard_text
            embed.set_footer(text=f"Top {limit} users • Requested by {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in leaderboard command: {e}")
            await self._error_response(interaction, "Failed to get leaderboard")
    
    @app_commands.command(name="daily", description="Claim your daily XP bonus")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily XP bonus."""
        try:
            # Check if already claimed
            user_data = await self.bot.db_manager.get_user(interaction.user.id)
            
            if not user_data:
                await self.bot.db_manager.create_user(interaction.user.id)
                user_data = await self.bot.db_manager.get_user(interaction.user.id)
            
            # Check if already claimed today
            from datetime import date
            today = date.today().isoformat()
            last_daily = user_data.get('last_daily_award_date')
            
            if last_daily == today:
                # Show next claim time
                embed = embed_helper.error_embed(
                    title="Daily Bonus Already Claimed",
                    description="You've already claimed your daily bonus today!\n\nCome back tomorrow for your next bonus."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Calculate bonus
            base_bonus = DAILY_CHECKIN_XP
            streak = user_data.get('streak', 0)
            streak_bonus = int(base_bonus * (streak * STREAK_BONUS_PERCENT / 100))
            total_bonus = base_bonus + streak_bonus
            
            # Award XP
            await self.bot.db_manager.update_user_xp(interaction.user.id, total_bonus)
            await self.bot.db_manager.set_daily_claimed(interaction.user.id, interaction.guild.id)
            new_streak = await self.bot.db_manager.increment_daily_streak(interaction.user.id, interaction.guild.id)
            
            # Create embed
            embed = create_embed(
                title="🎁 Daily Bonus Claimed!",
                description=f"You received **{total_bonus} XP** as your daily bonus!",
                color=COLORS["success"]
            )
            
            if streak_bonus > 0:
                embed.add_field(
                    name="🔥 Streak Bonus",
                    value=f"Day {new_streak} streak: +{streak_bonus} XP"
                )
            
            embed.add_field(
                name="💰 Breakdown",
                value=f"Base: {base_bonus} XP\nStreak Bonus: {streak_bonus} XP\nTotal: {total_bonus} XP"
            )
            
            embed.set_footer(text="Come back tomorrow for your next daily bonus!")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"{interaction.user.name} claimed daily bonus: {total_bonus} XP (streak: {new_streak})")
            
        except Exception as e:
            self.logger.error(f"Error in daily command: {e}")
            await self._error_response(interaction, "Failed to claim daily bonus")
    
    @app_commands.command(name="xpadmin", description="XP administration commands (Bot Owner only)")
    @app_commands.describe(
        action="What action would you like to perform?",
        user="User to perform action on",
        amount="Amount of XP to add/remove"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="reset", value="reset")
    ])
    async def xpadmin(self, interaction: discord.Interaction, action: str, user: discord.Member, amount: int = 0):
        """XP administration commands."""
        try:
            # Check permissions
            if not is_owner(interaction.user):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command is only available to the bot owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="Database is not available."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Route to appropriate handler
            if action == "add":
                await self._xpadmin_add(interaction, user, amount)
            elif action == "remove":
                await self._xpadmin_remove(interaction, user, amount)
            elif action == "set":
                await self._xpadmin_set(interaction, user, amount)
            elif action == "reset":
                await self._xpadmin_reset(interaction, user)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified action is not recognized."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            self.logger.error(f"Error in xpadmin command: {e}")
            await self._error_response(interaction, "Failed to execute XP admin command")
    
    async def _xpadmin_add(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Add XP to user."""
        try:
            if amount <= 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount must be greater than 0."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await self.bot.db_manager.update_user_xp(user.id, amount)
            
            embed = embed_helper.success_embed(
                title="✅ XP Added",
                description=f"Added {amount:,} XP to {user.mention}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Admin {interaction.user.name} added {amount} XP to {user.name}")
            
        except Exception as e:
            self.logger.error(f"Error adding XP: {e}")
            await self._error_response(interaction, "Failed to add XP")
    
    async def _xpadmin_remove(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Remove XP from user."""
        try:
            if amount <= 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount must be greater than 0."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get current XP
            user_data = await self.bot.db_manager.get_user(user.id)
            if not user_data or user_data.get('xp', 0) < amount:
                embed = embed_helper.error_embed(
                    title="Insufficient XP",
                    description=f"{user.mention} only has {user_data.get('xp', 0):,} XP."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            new_xp = user_data.get('xp', 0) - amount
            await self.bot.db_manager.update_user_xp(user.id, -amount)
            
            embed = embed_helper.success_embed(
                title="✅ XP Removed",
                description=f"Removed {amount:,} XP from {user.mention}\nNew total: {new_xp:,} XP"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Admin {interaction.user.name} removed {amount} XP from {user.name}")
            
        except Exception as e:
            self.logger.error(f"Error removing XP: {e}")
            await self._error_response(interaction, "Failed to remove XP")
    
    async def _xpadmin_set(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Set user XP to specific amount."""
        try:
            if amount < 0:
                embed = embed_helper.error_embed(
                    title="Invalid Amount",
                    description="Amount cannot be negative."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get current XP and calculate difference
            user_data = await self.bot.db_manager.get_user(user.id)
            current_xp = user_data.get('xp', 0) if user_data else 0
            diff = amount - current_xp
            
            if diff != 0:
                await self.bot.db_manager.update_user_xp(user.id, diff)
            
            embed = embed_helper.success_embed(
                title="✅ XP Set",
                description=f"Set {user.mention}'s XP to {amount:,}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Admin {interaction.user.name} set {user.name}'s XP to {amount}")
            
        except Exception as e:
            self.logger.error(f"Error setting XP: {e}")
            await self._error_response(interaction, "Failed to set XP")
    
    async def _xpadmin_reset(self, interaction: discord.Interaction, user: discord.Member):
        """Reset user XP and level."""
        try:
            await self.bot.db_manager.reset_user_xp(user.id)
            
            embed = embed_helper.success_embed(
                title="✅ XP Reset",
                description=f"Reset {user.mention}'s XP and level to 0"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.logger.info(f"Admin {interaction.user.name} reset {user.name}'s XP")
            
        except Exception as e:
            self.logger.error(f"Error resetting XP: {e}")
            await self._error_response(interaction, "Failed to reset XP")
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="XP Command Error",
            description=message
        )
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            pass

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    await bot.add_cog(XP(bot))