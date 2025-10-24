"""
XP and leveling system cog for MalaBoT.
Handles user XP gains, level progression, and XP administration.
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, List

from utils.logger import get_logger
from utils.helpers import (
    embed_helper, xp_helper, time_helper, cooldown_helper,
    create_embed, is_admin, permission_helper
)
from config.constants import COLORS, XP_TABLE, XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX, XP_COOLDOWN_SECONDS, DAILY_CHECKIN_XP, STREAK_BONUS_PERCENT
from config.settings import settings

class XP(commands.Cog):
    """XP and leveling system for users."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger('xp')
        self.message_cooldowns = {}  # User ID -> last message time
        self.daily_checkins = {}  # User ID -> last check-in date
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle message events for XP gains."""
        try:
            # Skip bot messages and DMs
            if message.author.bot or not isinstance(message.channel, discord.TextChannel):
                return
            
            # Skip if in safe mode
            if getattr(self.bot, 'safe_mode', False):
                return
            
            # Check cooldown for this user
            user_id = message.author.id
            current_time = datetime.now()
            
            if user_id in self.message_cooldowns:
                time_since_last = (current_time - self.message_cooldowns[user_id]).total_seconds()
                if time_since_last < XP_COOLDOWN_SECONDS:
                    return
            
            # Update cooldown
            self.message_cooldowns[user_id] = current_time
            
            # Get user data
            if not self.bot.db_manager:
                return
            
            user_data = await self.bot.db_manager.get_user(user_id)
            if not user_data:
                user_data = await self.bot.db_manager.create_user(user_id)
            
            # Check for daily check-in
            daily_bonus = 0
            streak_bonus_applied = False
            
            # Get daily channel from settings
            daily_channel_id = await self.bot.db_manager.get_setting('xp_daily_channel_id')
            is_daily_channel = daily_channel_id is None or message.channel.id == daily_channel_id
            
            today = current_time.date()
            last_daily = None
            
            if user_data.get('last_daily_award_date'):
                last_daily = datetime.strptime(user_data['last_daily_award_date'], '%Y-%m-%d').date()
            
            if is_daily_channel and (last_daily is None or last_daily < today):
                # Award daily check-in XP
                daily_bonus = DAILY_CHECKIN_XP
                
                # Calculate streak bonus
                streak_days = user_data.get('daily_streak', 0)
                if last_daily and (today - last_daily).days == 1:
                    # Consecutive day
                    streak_days += 1
                    streak_bonus = int(daily_bonus * (STREAK_BONUS_PERCENT / 100))
                    daily_bonus += streak_bonus
                    streak_bonus_applied = True
                    
                    # Update streak in database
                    conn = await self.bot.db_manager.get_connection()
                    await conn.execute(
                        "UPDATE users SET daily_streak = ?, last_daily_award_date = ? WHERE user_id = ?",
                        (streak_days, today.isoformat(), user_id)
                    )
                    await conn.commit()
                elif last_daily is None or (today - last_daily).days > 1:
                    # Streak broken or first time
                    streak_days = 1
                    conn = await self.bot.db_manager.get_connection()
                    await conn.execute(
                        "UPDATE users SET daily_streak = ?, last_daily_award_date = ? WHERE user_id = ?",
                        (streak_days, today.isoformat(), user_id)
                    )
                    await conn.commit()
                
                # Send daily check-in notification
                if daily_channel_id is None or message.channel.id == daily_channel_id:
                    daily_embed = embed_helper.xp_embed(
                        title="✨ Daily Check-in!",
                        description=f"You earned {daily_bonus} XP today{f' (+{streak_bonus} streak bonus 🔥)' if streak_bonus_applied else ''}!\nCurrent streak: {streak_days} days 🎯",
                        user=message.author
                    )
                    
                    try:
                        await message.channel.send(embed=daily_embed, delete_after=10)
                    except:
                        pass  # Don't fail if we can't send the message
                
                # Log daily check-in
                await self.bot.db_manager.log_event(
                    category='XP',
                    action='DAILY_CHECKIN',
                    user_id=user_id,
                    channel_id=message.channel.id,
                    details=f"XP: {daily_bonus}, Streak: {streak_days} days"
                )
            
            # Calculate XP gain
            xp_gained = random.randint(XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX) + daily_bonus
            
            # Update user XP
            updated_user = await self.bot.db_manager.update_user_xp(user_id, xp_gained)
            
            # Check for level up
            if updated_user['level'] > user_data['level']:
                await self._handle_level_up(message.author, updated_user['level'], message.channel)
            
            # Log XP gain
            if daily_bonus > 0:
                await self.bot.db_manager.log_event(
                    category='XP',
                    action='GAIN_WITH_DAILY',
                    user_id=user_id,
                    channel_id=message.channel.id,
                    details=f"XP: {xp_gained} (Message: {xp_gained - daily_bonus}, Daily: {daily_bonus})"
                )
            else:
                await self.bot.db_manager.log_event(
                    category='XP',
                    action='GAIN',
                    user_id=user_id,
                    channel_id=message.channel.id,
                    details=f"XP: {xp_gained}"
                )
        
        except Exception as e:
            self.logger.error(f"Error in on_message XP handler: {e}")
    
    async def _handle_level_up(self, member: discord.Member, new_level: int, channel: discord.TextChannel):
        """Handle user level up."""
        try:
            # Get XP for next level
            xp_needed_for_next = xp_helper.calculate_xp_for_next_level(new_level)
            user_data = await self.bot.db_manager.get_user(member.id)
            
            if not user_data:
                return
            
            current_xp = user_data['xp']
            xp_at_current_level = XP_TABLE.get(new_level, 0)
            xp_progress = current_xp - xp_at_current_level
            
            # Create level up embed
            embed = embed_helper.xp_embed(
                title="🎉 Level Up!",
                description=f"Congratulations {member.mention}! You've reached **Level {new_level}**! 🎊",
                user=member
            )
            
            # Add XP progress bar
            progress_bar = xp_helper.get_xp_progress_bar(xp_progress, xp_needed_for_next)
            embed.add_field(
                name="📊 XP Progress",
                value=f"**{xp_progress} / {xp_needed_for_next} XP to next level**\n{progress_bar}",
                inline=False
            )
            
            # Add rewards information
            rewards = []
            from config.constants import LEVEL_ROLE_MAP
            
            if new_level in LEVEL_ROLE_MAP:
                role_name_or_id = LEVEL_ROLE_MAP[new_level]
                if role_name_or_id:
                    rewards.append(f"🏅 Special Role")
            
            if new_level % 10 == 0:
                rewards.append("⭐ Milestone Achievement")
            
            if new_level >= 50:
                rewards.append("👑 Elite Status")
            
            if rewards:
                embed.add_field(
                    name="🎁 Rewards",
                    value="\n".join(rewards),
                    inline=False
                )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            embed.set_footer(text="Keep being active to earn more XP!")
            
            # Send level up message
            await channel.send(embed=embed)
            
            # Assign level role if applicable
            if isinstance(member, discord.Member):
                role_assigned = await xp_helper.assign_level_role(member, new_level)
                if role_assigned:
                    try:
                        await channel.send(
                            f"🎭 {member.mention} has been assigned the **{role_assigned.name}** role!",
                            delete_after=30
                        )
                    except:
                        pass
            
            # Log level up
            await self.bot.db_manager.log_event(
                category='XP',
                action='LEVELUP',
                user_id=member.id,
                channel_id=channel.id,
                guild_id=channel.guild.id,
                details=f"Level: {new_level}, XP: {current_xp}"
            )
        
        except Exception as e:
            self.logger.error(f"Error handling level up for {member.id}: {e}")
    
    @app_commands.command(name="xp", description="XP system commands")
    @app_commands.describe(
        action="What XP action would you like to perform?"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="rank", value="rank"),
        app_commands.Choice(name="leaderboard", value="leaderboard")
    ])
    async def xp(self, interaction: discord.Interaction, action: str):
        """XP system main command."""
        try:
            if action == "rank":
                await self._xp_rank(interaction)
            elif action == "leaderboard":
                await self._xp_leaderboard(interaction)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified XP action is not available."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            self.logger.error(f"Error in xp command: {e}")
            await self._error_response(interaction, "Failed to process XP command")
    
    async def _xp_rank(self, interaction: discord.Interaction):
        """Show user's XP rank and level."""
        try:
            user_id = interaction.user.id
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="XP system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get user data
            user_data = await self.bot.db_manager.get_user(user_id)
            if not user_data:
                user_data = await self.bot.db_manager.create_user(user_id)
            
            # Get user's rank on server
            rank = await self._get_user_rank(user_id)
            
            # Get XP for current and next level
            current_level = user_data['level']
            current_xp = user_data['xp']
            
            xp_at_current_level = XP_TABLE.get(current_level, 0)
            xp_needed_for_next = xp_helper.calculate_xp_for_next_level(current_level)
            xp_progress = current_xp - xp_at_current_level
            
            # Create rank embed
            embed = embed_helper.xp_embed(
                title=f"🏆 {interaction.user.display_name}'s XP Rank",
                user=interaction.user
            )
            
            # Basic stats
            embed.add_field(
                name="📊 Statistics",
                value=f"**Level:** {current_level}\n"
                      f"**Total XP:** {current_xp:,}\n"
                      f"**Server Rank:** #{rank}\n"
                      f"**Messages:** {user_data.get('total_messages', 0):,}",
                inline=False
            )
            
            # Progress to next level
            if current_level < max(XP_TABLE.keys()):
                progress_bar = xp_helper.get_xp_progress_bar(xp_progress, xp_needed_for_next)
                embed.add_field(
                    name="📈 Progress to Next Level",
                    value=f"**{xp_progress} / {xp_needed_for_next} XP**\n{progress_bar}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="👑 Maximum Level",
                    value="You've reached the maximum level! Congratulations! 🎉",
                    inline=False
                )
            
            # Daily streak info
            daily_streak = user_data.get('daily_streak', 0)
            if daily_streak > 0:
                embed.add_field(
                    name="🔥 Daily Streak",
                    value=f"**{daily_streak} days** consecutive check-ins!\nKeep it up for streak bonuses!",
                    inline=False
                )
            
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
            embed.set_footer(text="Earn XP by being active in the server!")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Log rank command usage
            await self.bot.db_manager.log_event(
                category='XP',
                action='RANK_CHECK',
                user_id=user_id,
                channel_id=interaction.channel.id
            )
        
        except Exception as e:
            self.logger.error(f"Error in xp rank command: {e}")
            raise
    
    async def _xp_leaderboard(self, interaction: discord.Interaction):
        """Show XP leaderboard."""
        try:
            if not isinstance(interaction.channel, discord.TextChannel):
                await self._error_response(interaction, "This command can only be used in a server")
                return
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="XP system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Get top users
            conn = await self.bot.db_manager.get_connection()
            cursor = await conn.execute("""
                SELECT user_id, xp, level, total_messages 
                FROM users 
                ORDER BY xp DESC, level DESC 
                LIMIT 15
            """)
            
            rows = await cursor.fetchall()
            
            if not rows:
                embed = embed_helper.info_embed(
                    title="🏆 XP Leaderboard",
                    description="No users have earned XP yet!"
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Create leaderboard embed
            embed = embed_helper.create_embed(
                title=f"🏆 XP Leaderboard - {interaction.guild.name}",
                color=COLORS["xp"]
            )
            
            # Process leaderboard entries
            leaderboard_text = ""
            medals = ["🥇", "🥈", "🥉"]
            
            for i, (user_id, xp, level, messages) in enumerate(rows, 1):
                try:
                    user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                    user_name = user.display_name if user else f"User {user_id}"
                    
                    # Get medal for top 3
                    medal = medals[i-1] if i <= 3 else f"#{i}"
                    
                    leaderboard_text += f"{medal} **{user_name}** - Level {level} ({xp:,} XP)\n"
                    
                    # Limit to 10 entries in embed
                    if i >= 10:
                        break
                        
                except:
                    leaderboard_text += f"#{i} Unknown User - Level {level} ({xp:,} XP)\n"
            
            embed.description = leaderboard_text
            
            # Add statistics
            total_users = len(rows)
            top_xp = rows[0][1] if rows else 0
            
            embed.add_field(
                name="📊 Leaderboard Stats",
                value=f"Total Users: {total_users}\n"
                      f"Top XP: {top_xp:,}\n"
                      f"Updated: {time_helper.get_discord_timestamp(datetime.now(), 'R')}",
                inline=False
            )
            
            embed.set_footer(text="Leaderboard updates in real-time • Earn XP by being active!")
            
            await interaction.response.send_message(embed=embed)
            
            # Log leaderboard command usage
            await self.bot.db_manager.log_event(
                category='XP',
                action='LEADERBOARD_VIEW',
                user_id=interaction.user.id,
                channel_id=interaction.channel.id
            )
        
        except Exception as e:
            self.logger.error(f"Error in xp leaderboard command: {e}")
            raise
    
    @app_commands.command(name="xpadmin", description="XP administration commands (Admin only)")
    @app_commands.describe(
        action="Admin action to perform"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="set", value="set"),
        app_commands.Choice(name="reset", value="reset"),
        app_commands.Choice(name="setchannel", value="setchannel")
    ])
    async def xpadmin(self, interaction: discord.Interaction, action: str):
        """XP administration commands."""
        try:
            # Check permissions
            if not is_admin(interaction.user):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command is only available to administrators."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error",
                    description="XP system is currently unavailable."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if action == "setchannel":
                await self._xpadmin_setchannel(interaction)
            else:
                # These actions require additional parameters
                await interaction.response.send_message(
                    f"This action requires additional parameters. Please use the full command format.",
                    ephemeral=True
                )
        
        except Exception as e:
            self.logger.error(f"Error in xpadmin command: {e}")
            await self._error_response(interaction, "Failed to process XP admin command")
    
    async def _xpadmin_setchannel(self, interaction: discord.Interaction):
        """Set daily XP channel."""
        try:
            channel_id = interaction.channel.id
            
            await self.bot.db_manager.set_setting('xp_daily_channel_id', channel_id)
            
            embed = embed_helper.success_embed(
                title="✅ Daily XP Channel Set",
                description=f"This channel ({interaction.channel.mention}) has been set as the daily check-in channel.\n\nUsers will now earn daily bonus XP only when messaging in this channel."
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log admin action
            await self.bot.db_manager.log_event(
                category='ADMIN',
                action='XP_CHANNEL_SET',
                user_id=interaction.user.id,
                channel_id=channel_id,
                guild_id=interaction.guild.id,
                details=f"Daily XP channel set to {channel_id}"
            )
        
        except Exception as e:
            self.logger.error(f"Error setting XP channel: {e}")
            raise
    
    async def _get_user_rank(self, user_id: int) -> int:
        """Get user's rank on the server."""
        try:
            if not self.bot.db_manager:
                return 0
            
            conn = await self.bot.db_manager.get_connection()
            cursor = await conn.execute("""
                SELECT COUNT(*) + 1 
                FROM users 
                WHERE (xp > (SELECT xp FROM users WHERE user_id = ?)) 
                   OR (xp = (SELECT xp FROM users WHERE user_id = ?) AND level > (SELECT level FROM users WHERE user_id = ?))
            """, (user_id, user_id, user_id))
            
            rank = (await cursor.fetchone())[0]
            return rank
        
        except Exception as e:
            self.logger.error(f"Error getting user rank: {e}")
            return 0
    
    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="XP System Error",
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