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
            
            xp_per_message = int(xp_per_message)
            xp_cooldown = int(xp_cooldown)
            
            # Check cooldown
            if user_id in self.last_xp_time:
                time_diff = current_time - self.last_xp_time[user_id]
                if time_diff < xp_cooldown:
                    return
            
            # Award XP
            await self.bot.db_manager.update_user_xp(message.author.id, xp_per_message)
            
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
            guild_id = guild.id
            
            # Get configured level-up channel
            xp_channel_id = await self.bot.db_manager.get_setting(f"xp_channel_{guild_id}")
            
            # Get configured level-up message
            levelup_message = await self.bot.db_manager.get_setting(f"xp_levelup_message_{guild_id}")
            
            # Use default channel if not configured
            if xp_channel_id:
                channel = guild.get_channel(int(xp_channel_id))
            else:
                channel = guild.system_channel or guild.text_channels[0]
            
            if not channel:
                self.logger.warning(f"No channel found for level-up message in {guild.name}")
                return
            
            # Use custom message if configured, otherwise use default
            if levelup_message:
                # Replace variables in custom message
                message_text = levelup_message.replace("{member}", member.mention)
                message_text = message_text.replace("{level}", str(new_level))
                description = message_text
            else:
                description = f"{member.mention} has reached level **{new_level}**!"
            
            embed = create_embed(
                title=f"🎉 Level Up!",
                description=description,
                color=COLORS["success"]
            )
            
            await channel.send(embed=embed)
            
            # Update database
            await self.bot.db_manager.update_user_xp(member.id, 0)  # Update level in database
            
            # Assign level role if configured
            await self._assign_level_role(member, new_level)
            
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
    
    @app_commands.command(name="xpadd", description="Add XP to a user (Server Owner only)")
    @app_commands.describe(
        user="User to add XP to",
        amount="Amount of XP to add"
    )
    async def xpadd(self, interaction: discord.Interaction, user: discord.Member, amount: int):
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
            
            await self._xpadmin_add(interaction, user, amount)
        except Exception as e:
            self.logger.error(f"Error in xpadd command: {e}")
            await self._error_response(interaction, "Failed to add XP")
    
    @app_commands.command(name="xpremove", description="Remove XP from a user (Server Owner only)")
    @app_commands.describe(
        user="User to remove XP from",
        amount="Amount of XP to remove"
    )
    async def xpremove(self, interaction: discord.Interaction, user: discord.Member, amount: int):
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
            
            await self._xpadmin_remove(interaction, user, amount)
        except Exception as e:
            self.logger.error(f"Error in xpremove command: {e}")
            await self._error_response(interaction, "Failed to remove XP")
    
    @app_commands.command(name="xpset", description="Set user XP to a specific amount (Server Owner only)")
    @app_commands.describe(
        user="User to set XP for",
        amount="Amount of XP to set"
    )
    async def xpset(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Set user XP to a specific amount."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await self._xpadmin_set(interaction, user, amount)
        except Exception as e:
            self.logger.error(f"Error in xpset command: {e}")
            await self._error_response(interaction, "Failed to set XP")
    
    @app_commands.command(name="xpreset", description="Reset user XP to 0 (Server Owner only)")
    @app_commands.describe(
        user="User to reset XP for"
    )
    async def xpreset(self, interaction: discord.Interaction, user: discord.Member):
        """Reset user XP to 0."""
        try:
            # Check server owner permissions
            if interaction.guild.owner_id != interaction.user.id:
                embed = embed_helper.error_embed(
                    title="🚫 Permission Denied",
                    description="This command is only available to the server owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await self._xpadmin_reset(interaction, user)
        except Exception as e:
            self.logger.error(f"Error in xpreset command: {e}")
            await self._error_response(interaction, "Failed to reset XP")
    

    # xpconfig command removed - use /setup instead
    

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
    
    async def _assign_level_role(self, member: discord.Member, level: int):
        """Assign role based on level if configured."""
        try:
            guild_id = member.guild.id
            
            # Get level roles from database
            level_roles_data = await self.bot.db_manager.get_setting(f"xp_level_roles_{guild_id}")
            
            if not level_roles_data:
                return
            
            # Parse level roles (format: "level:role_id,level:role_id")
            level_roles = {}
            for pair in level_roles_data.split(","):
                if ":" in pair:
                    lvl, role_id = pair.split(":")
                    level_roles[int(lvl)] = int(role_id)
            
            # Check if this level has a role
            if level in level_roles:
                role = member.guild.get_role(level_roles[level])
                if role and role not in member.roles:
                    await member.add_roles(role, reason=f"Reached level {level}")
                    self.logger.info(f"Assigned {role.name} to {member.name} for reaching level {level}")
        
        except Exception as e:
            self.logger.error(f"Error assigning level role: {e}")
    
    @app_commands.command(name="xplevelrole", description="Manage level role rewards (Admin only)")
    @app_commands.describe(
        action="Action to perform",
        level="Level to assign role at",
        role="Role to assign"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="List", value="list")
    ])
    async def xplevelrole(
        self, 
        interaction: discord.Interaction, 
        action: str,
        level: Optional[int] = None,
        role: Optional[discord.Role] = None
    ):
        """Manage level role rewards."""
        try:
            # Check permissions
            if not interaction.user.guild_permissions.administrator:
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="You need administrator permissions to manage level roles."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            
            guild_id = interaction.guild.id
            
            if action == "list":
                await self._list_level_roles(interaction, guild_id)
            elif action == "add":
                if level is None or role is None:
                    embed = embed_helper.error_embed(
                        title="Missing Parameters",
                        description="Please provide both level and role for adding."
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                await self._add_level_role(interaction, guild_id, level, role)
            elif action == "remove":
                if level is None:
                    embed = embed_helper.error_embed(
                        title="Missing Parameter",
                        description="Please provide the level to remove."
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                await self._remove_level_role(interaction, guild_id, level)
        
        except Exception as e:
            self.logger.error(f"Error in xplevelrole command: {e}")
            await self._error_response(interaction, "Failed to manage level roles")
    
    async def _list_level_roles(self, interaction: discord.Interaction, guild_id: int):
        """List all configured level roles."""
        try:
            level_roles_data = await self.bot.db_manager.get_setting(f"xp_level_roles_{guild_id}")
            
            if not level_roles_data:
                embed = embed_helper.info_embed(
                    title="Level Roles",
                    description="No level roles configured yet.\n\nUse `/xplevelrole add` to add level rewards."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Parse and display level roles
            level_roles = {}
            for pair in level_roles_data.split(","):
                if ":" in pair:
                    lvl, role_id = pair.split(":")
                    level_roles[int(lvl)] = int(role_id)
            
            # Sort by level
            sorted_roles = sorted(level_roles.items())
            
            description = "**Configured Level Roles:**\n\n"
            for lvl, role_id in sorted_roles:
                role = interaction.guild.get_role(role_id)
                if role:
                    description += f"Level **{lvl}**: {role.mention}\n"
                else:
                    description += f"Level **{lvl}**: *Role not found (ID: {role_id})*\n"
            
            embed = embed_helper.info_embed(
                title="🏆 Level Roles",
                description=description
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error listing level roles: {e}")
            await self._error_response(interaction, "Failed to list level roles")
    
    async def _add_level_role(self, interaction: discord.Interaction, guild_id: int, level: int, role: discord.Role):
        """Add a level role reward."""
        try:
            level_roles_data = await self.bot.db_manager.get_setting(f"xp_level_roles_{guild_id}") or ""
            
            # Parse existing level roles
            level_roles = {}
            if level_roles_data:
                for pair in level_roles_data.split(","):
                    if ":" in pair:
                        lvl, role_id = pair.split(":")
                        level_roles[int(lvl)] = int(role_id)
            
            # Add or update the level role
            level_roles[level] = role.id
            
            # Convert back to string format
            new_data = ",".join([f"{lvl}:{role_id}" for lvl, role_id in level_roles.items()])
            
            # Save to database
            await self.bot.db_manager.set_setting(f"xp_level_roles_{guild_id}", new_data)
            
            embed = embed_helper.success_embed(
                title="✅ Level Role Added",
                description=f"Users will now receive {role.mention} when they reach level **{level}**."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            self.logger.info(f"Added level role: Level {level} -> {role.name} in {interaction.guild.name}")
        
        except Exception as e:
            self.logger.error(f"Error adding level role: {e}")
            await self._error_response(interaction, "Failed to add level role")
    
    async def _remove_level_role(self, interaction: discord.Interaction, guild_id: int, level: int):
        """Remove a level role reward."""
        try:
            level_roles_data = await self.bot.db_manager.get_setting(f"xp_level_roles_{guild_id}")
            
            if not level_roles_data:
                embed = embed_helper.error_embed(
                    title="No Level Roles",
                    description="No level roles configured yet."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Parse existing level roles
            level_roles = {}
            for pair in level_roles_data.split(","):
                if ":" in pair:
                    lvl, role_id = pair.split(":")
                    level_roles[int(lvl)] = int(role_id)
            
            # Check if level exists
            if level not in level_roles:
                embed = embed_helper.error_embed(
                    title="Level Not Found",
                    description=f"No role configured for level **{level}**."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Remove the level role
            del level_roles[level]
            
            # Convert back to string format
            new_data = ",".join([f"{lvl}:{role_id}" for lvl, role_id in level_roles.items()])
            
            # Save to database
            await self.bot.db_manager.set_setting(f"xp_level_roles_{guild_id}", new_data)
            
            embed = embed_helper.success_embed(
                title="✅ Level Role Removed",
                description=f"Removed role reward for level **{level}**."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            self.logger.info(f"Removed level role for level {level} in {interaction.guild.name}")
        
        except Exception as e:
            self.logger.error(f"Error removing level role: {e}")
            await self._error_response(interaction, "Failed to remove level role")

async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    await bot.add_cog(XP(bot))