"""
XP and leveling system cog for MalaBoT.
Handles user XP gains, level progression, and XP administration.
"""
# Test comment - verifying deployment workflow
import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from config.constants import (
    COLORS,
    DAILY_CHECKIN_XP,
    STREAK_BONUS_PERCENT,
    XP_COOLDOWN_SECONDS,
    XP_PER_MESSAGE,
    XP_PER_REACTION,
    XP_PER_VOICE_MINUTE,
    XP_TABLE,
)
from utils.helpers import (
    create_embed,
    embed_helper,
)
from utils.logger import get_logger


class XPGroup(app_commands.Group):
    """XP command group"""

    def __init__(self, cog):
        super().__init__(name="xp", description="XP and leveling system commands")
        self.cog = cog

    @app_commands.command(
        name="rank", description="Check your or another user's rank and XP"
    )
    @app_commands.describe(user="User to check (leave empty for yourself)")
    async def rank(
        self, interaction: discord.Interaction, user: Optional[discord.Member] = None
    ):
        """Check XP rank."""
        try:
            # Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)
            
            target = user or interaction.user

            # Get user stats from database
            xp = await self.cog.bot.db_manager.get_user_xp(target.id, interaction.guild.id)
            level = await self.cog.bot.db_manager.get_user_level(target.id, interaction.guild.id)

            # Get rank
            rank = await self.cog.bot.db_manager.get_user_rank(
                target.id, interaction.guild.id
            )

            # Calculate XP for next level using XP_TABLE
            if level < len(XP_TABLE):
                next_level_xp = XP_TABLE[min(level + 1, len(XP_TABLE) - 1)]
                current_level_xp = XP_TABLE[level]
            else:
                # For very high levels, use a formula
                next_level_xp = 1000 * (level + 1) * level
                current_level_xp = 1000 * level * (level - 1)
            xp_needed = next_level_xp - xp
            xp_progress = xp - current_level_xp
            xp_total_needed = next_level_xp - current_level_xp

            # Create progress bar
            progress = int((xp_progress / xp_total_needed) * 20)
            progress_bar = "█" * progress + "░" * (20 - progress)

            embed = create_embed(
                title=f"📊 {target.display_name}'s Rank",
                description=f"**Rank:** #{rank}\n**Level:** {level}\n**XP:** {xp:,} / {next_level_xp:,}\n\n{progress_bar}\n\n**XP Needed:** {xp_needed:,}",
                color=COLORS["primary"],
            )

            embed.set_thumbnail(url=target.display_avatar.url)

            await interaction.followup.send(embed=embed, ephemeral=True)


        except Exception as e:
            self.cog.logger.error(f"Error in rank command: {e}")
            embed = embed_helper.error_embed(
                "Error", "Failed to fetch rank information."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="leaderboard", description="Show server XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Show XP leaderboard."""
        try:
            # Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)
            
            # Get top users by XP for this guild only
            guild_member_ids = [member.id for member in interaction.guild.members]
            if not guild_member_ids:
                embed = create_embed(
                    title="\ud83c\udfc6 XP Leaderboard",
                    description="No guild members found!",
                    color=COLORS["warning"],
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

                return

            conn = await self.cog.bot.db_manager.get_connection()
            placeholders = ",".join(["?" for _ in guild_member_ids])
            cursor = await conn.execute(
                f"""SELECT user_id, xp, level
                   FROM users
                   WHERE user_id IN ({placeholders}) AND xp > 0
                   ORDER BY xp DESC
                   LIMIT 10""",
                guild_member_ids,
            )
            rows = await cursor.fetchall()

            if not rows:
                embed = create_embed(
                    title="🏆 XP Leaderboard",
                    description="No users have XP yet!",
                    color=COLORS["warning"],
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            description = ""
            for i, (user_id, xp, level) in enumerate(rows, 1):
                user = interaction.guild.get_member(user_id)
                if user:
                    medal = ""
                    if i == 1:
                        medal = "🥇"
                    elif i == 2:
                        medal = "🥈"
                    elif i == 3:
                        medal = "🥉"
                    description += (
                        f"{medal} **{i}.** {user.mention} - Level {level} ({xp:,} XP)\n"
                    )

            embed = create_embed(
                title="🏆 XP Leaderboard",
                description=description,
                color=COLORS["primary"],
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.cog.logger.error(f"Error in leaderboard command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to fetch leaderboard.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="checkin", description="Claim your daily XP bonus")
    async def checkin(self, interaction: discord.Interaction):
        """Daily checkin for XP bonus."""
        await interaction.response.defer(ephemeral=True)

        try:
            user_id = interaction.user.id
            today = datetime.datetime.now().date()

            # Check last checkin (per-server)
            checkin_data = await self.cog.bot.db_manager.get_user_checkin(user_id, interaction.guild.id)
            
            if checkin_data:
                last_checkin_str = checkin_data[2]  # last_checkin is at index 2
                last_checkin = datetime.datetime.strptime(last_checkin_str, "%Y-%m-%d").date()
                streak = checkin_data[3]  # checkin_streak is at index 3
                if last_checkin == today:
                    embed = create_embed(
                        title="✅ Already Checked In",
                        description="You've already claimed your daily bonus today!",
                        color=COLORS["warning"],
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Calculate streak
                streak = streak if (today - last_checkin).days == 1 else 0
            else:
                streak = 0

            if row:
                last_checkin = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
                if last_checkin == today:
                    embed = create_embed(
                        title="✅ Already Checked In",
                        description="You've already claimed your daily bonus today!",
                        color=COLORS["warning"],
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Calculate streak
                streak = row[1] if (today - last_checkin).days == 1 else 0
            else:
                streak = 0

            streak += 1

            # Calculate bonus with streak
            bonus = DAILY_CHECKIN_XP
            if streak > 1:
                bonus = int(bonus * (1 + (STREAK_BONUS_PERCENT / 100 * (streak - 1))))

            # Give XP
            new_xp, new_level, leveled_up = await self.cog.bot.db_manager.update_user_xp(user_id, bonus, interaction.guild.id)

            # Check for level-up and assign roles
            if leveled_up:
                await self.cog._check_level_up(interaction.user)

            # Update checkin record
            # Update checkin record (per-server)
            await self.cog.bot.db_manager.update_user_checkin(
                user_id, interaction.guild.id, today.isoformat(), streak
            )

            embed = create_embed(
                title="✅ Daily Check-in Complete!",
                description=f"You've received **{bonus:,} XP**!\nCurrent streak: **{streak}** days",
                color=COLORS["success"],
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.cog.logger.error(f"Error in checkin command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to process checkin.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="add", description="Add XP to a user (Server Owner only)"
    )
    @app_commands.describe(user="User to add XP to", amount="Amount of XP to add")
    @app_commands.checks.has_permissions(administrator=True)
    async def add(
        self, interaction: discord.Interaction, user: discord.Member, amount: int
    ):
        """Add XP to a user."""
        if not interaction.user.guild_permissions.administrator:
            embed = embed_helper.error_embed(
                "Permission Denied",
                "Only server owners and administrators can use this command.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount <= 0:
            embed = embed_helper.error_embed(
                "Invalid Amount", "XP amount must be positive."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            new_xp, new_level, leveled_up = await self.cog.bot.db_manager.update_user_xp(user.id, amount, interaction.guild.id)
            if leveled_up:
                await self.cog._check_level_up(user)
            embed = create_embed(
                title="✅ XP Added",
                description=f"Added **{amount:,} XP** to {user.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in add command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to add XP.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="add-all",
        description="Add XP to ALL users in the server (Server Owner only)",
    )
    @app_commands.describe(
        amount="Amount of XP to add to everyone", confirm="Type 'yes' to confirm"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_all(
        self, interaction: discord.Interaction, amount: int, confirm: str
    ):
        """Add XP to all users."""
        if not interaction.user.guild_permissions.administrator:
            embed = embed_helper.error_embed(
                "Permission Denied", "Only the server owner can use this command."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if confirm.lower() != "yes":
            embed = embed_helper.error_embed(
                "Confirmation Required",
                "You must type 'yes' in the confirm field to add XP to all users.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount <= 0:
            embed = embed_helper.error_embed(
                "Invalid Amount", "XP amount must be positive."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Add XP to all users in the server
            for member in interaction.guild.members:
                if not member.bot:
                    new_xp, new_level, leveled_up = await self.cog.bot.db_manager.update_user_xp(member.id, amount, interaction.guild.id)

                    # Check for level-up and assign roles
                    if leveled_up:
                        await self.cog._check_level_up(member)

            embed = create_embed(
                title="✅ XP Added to All Users",
                description=f"Added **{amount:,} XP** to all users in the server",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in add_all command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to add XP to all users.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="remove", description="Remove XP from a user (Server Owner only)"
    )
    @app_commands.describe(
        user="User to remove XP from", amount="Amount of XP to remove"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def remove(
        self, interaction: discord.Interaction, user: discord.Member, amount: int
    ):
        """Remove XP from a user."""
        if not interaction.user.guild_permissions.administrator:
            embed = embed_helper.error_embed(
                "Permission Denied",
                "Only server owners and administrators can use this command.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount <= 0:
            embed = embed_helper.error_embed(
                "Invalid Amount", "XP amount must be positive."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await self.cog.bot.db_manager.remove_user_xp(user.id, interaction.guild.id, amount)
            embed = create_embed(
                title="✅ XP Removed",
                description=f"Removed **{amount:,} XP** from {user.mention}",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in remove command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to remove XP.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="set", description="Set user XP to a specific amount (Server Owner only)"
    )
    @app_commands.describe(user="User to set XP for", amount="Amount of XP to set")
    @app_commands.checks.has_permissions(administrator=True)
    async def set(
        self, interaction: discord.Interaction, user: discord.Member, amount: int
    ):
        """Set user XP."""
        if not interaction.user.guild_permissions.administrator:
            embed = embed_helper.error_embed(
                "Permission Denied",
                "Only server owners and administrators can use this command.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount < 0:
            embed = embed_helper.error_embed(
                "Invalid Amount", "XP amount cannot be negative."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            old_level = await self.cog.bot.db_manager.get_user_level(user.id, interaction.guild.id)
            await self.cog.bot.db_manager.set_user_xp(user.id, interaction.guild.id, amount)
            new_level = await self.cog.bot.db_manager.get_user_level(user.id, interaction.guild.id)
            
            # Check if leveled up
            if new_level > old_level:
                await self.cog._check_level_up(user)
            
            embed = create_embed(
                title="✅ XP Set",
                description=f"Set {user.mention}'s XP to **{amount:,}**",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in set command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to set XP.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="reset", description="Reset a user's XP to 0 (Server Owner only)"
    )
    @app_commands.describe(user="User to reset XP for")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction, user: discord.Member):
        """Reset user XP."""
        if not interaction.user.guild_permissions.administrator:
            embed = embed_helper.error_embed(
                "Permission Denied",
                "Only server owners and administrators can use this command.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await self.cog.bot.db_manager.set_user_xp(user.id, interaction.guild.id, 0)
            embed = create_embed(
                title="✅ XP Reset",
                description=f"Reset {user.mention}'s XP to **0**",
                color=COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            self.cog.logger.error(f"Error in reset command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to reset XP.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="reset-all", description="Reset ALL users' XP to 0 (Server Owner only)"
    )
    async def reset_all(self, interaction: discord.Interaction):
        """Reset all users' XP to 0."""
        # Check if user is server owner
        if interaction.user.id != interaction.guild.owner_id:
            embed = embed_helper.error_embed(
                "Permission Denied",
                "Only the server owner can use this command.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Defer the response since this might take a while
            await interaction.response.defer(ephemeral=True)

            # Reset XP for all users in the database
            conn = await self.cog.bot.db_manager.get_connection()
            await conn.execute("UPDATE users SET xp = 0, level = 0")
            await conn.commit()

            # Get count of affected users
            cursor = await conn.execute("SELECT COUNT(*) FROM users")
            count = (await cursor.fetchone())[0]

            embed = create_embed(
                title="✅ All XP Reset",
                description=f"Successfully reset XP to 0 for **{count}** users in the database.",
                color=COLORS["success"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            # Log the action
            await self.cog.bot.db_manager.log_event(
                category="XP",
                action="RESET_ALL_XP",
                user_id=interaction.user.id,
                guild_id=interaction.guild.id,
                details=f"Reset all users' XP to 0",
            )

        except Exception as e:
            self.cog.logger.error(f"Error in reset_all command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to reset all users' XP.")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="reset-checkins",
        description="Reset ALL users' daily check-in streaks (Server Owner only)",
    )
    async def reset_checkins(self, interaction: discord.Interaction):
        """Reset all users' check-in streaks."""
        # Check if user is server owner
        if interaction.user.id != interaction.guild.owner_id:
            embed = embed_helper.error_embed(
                "Permission Denied",
                "Only the server owner can use this command.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Defer the response since this might take a while
            await interaction.response.defer(ephemeral=True)

            # Reset all check-in streaks
            conn = await self.cog.bot.db_manager.get_connection()
            
            # Get count before deletion
            cursor = await conn.execute("SELECT COUNT(*) FROM daily_checkins")
            count = (await cursor.fetchone())[0]
            
            # Delete all check-in records
            await conn.execute("DELETE FROM daily_checkins")
            await conn.commit()

            embed = create_embed(
                title="✅ All Check-ins Reset",
                description=f"Successfully reset check-in streaks for **{count}** users.\nAll users can now check in again and start fresh streaks.",
                color=COLORS["success"],
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            # Log the action
            await self.cog.bot.db_manager.log_event(
                category="XP",
                action="RESET_ALL_CHECKINS",
                user_id=interaction.user.id,
                guild_id=interaction.guild.id,
                details=f"Reset all users' check-in streaks",
            )

        except Exception as e:
            self.cog.logger.error(f"Error in reset_checkins command: {e}")
            embed = embed_helper.error_embed(
                "Error", "Failed to reset all check-in streaks."
            )
            await interaction.followup.send(embed=embed, ephemeral=True)





class XP(commands.Cog):
    """XP and leveling system."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger("xp")
        self.last_xp_time = {}  # Track last XP gain time per user
        self.level_up_sent = {}  # Track level-up messages sent (user_id: level)

    async def cog_unload(self):
        """Remove the command group when cog is unloaded."""
        if hasattr(self, "_xp_group"):
            self.bot.tree.remove_command(self._xp_group.name)

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

            # Check if message XP is enabled
            message_xp_enabled = await self.bot.db_manager.get_setting("xp_message_enabled", message.guild.id)
            if message_xp_enabled == "false":
                return
            
            # Get XP amount from database or use default
            xp_amount_str = await self.bot.db_manager.get_setting("xp_per_message", message.guild.id)
            xp_amount = int(xp_amount_str) if xp_amount_str else XP_PER_MESSAGE
            
            if xp_amount <= 0:
                return

            # Award XP and check for level up
            new_xp, new_level, leveled_up = await self.bot.db_manager.update_user_xp(
                user_id, xp_amount, message.guild.id
            )
            self.last_xp_time[user_id] = current_time

            # Check and assign level roles
            if leveled_up:
                await self._check_level_up(message.author)

        except Exception as e:
            self.logger.error(f"Error awarding message XP: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Award XP when a user's message receives a reaction."""
        try:
            # Ignore bot reactions
            if payload.user_id == self.bot.user.id:
                return

            # Get channel and message
            channel = self.bot.get_channel(payload.channel_id)
            if not channel:
                return

            message = await channel.fetch_message(payload.message_id)
            if not message or message.author.bot:
                return

            # Check if reaction XP is enabled
            reaction_xp_enabled = await self.bot.db_manager.get_setting("xp_reaction_enabled", message.guild.id)
            if reaction_xp_enabled == "false":
                return
            
            # Get XP amount from database or use default
            xp_amount_str = await self.bot.db_manager.get_setting("xp_per_reaction", message.guild.id)
            xp_amount = int(xp_amount_str) if xp_amount_str else XP_PER_REACTION
            
            if xp_amount <= 0:
                return

            # Award XP to message author
            new_xp, new_level, leveled_up = await self.bot.db_manager.update_user_xp(message.author.id, xp_amount, message.guild.id)
            
            # Check for level-up
            if leveled_up:
                await self._check_level_up(message.author)

        except Exception as e:
            self.logger.error(f"Error awarding reaction XP: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Award XP for time spent in voice chat."""
        try:
            # Check if user joined a voice channel
            if before.channel is None and after.channel is not None and not member.bot:
                # Start tracking voice time
                if not hasattr(self.bot, "voice_time"):
                    self.bot.voice_time = {}
                self.bot.voice_time[member.id] = datetime.datetime.now()

            # Check if user left a voice channel
            elif (
                before.channel is not None and after.channel is None and not member.bot
            ):
                # Calculate time spent and award XP
                if hasattr(self.bot, "voice_time") and member.id in self.bot.voice_time:
                    time_spent = (
                        datetime.datetime.now() - self.bot.voice_time[member.id]
                    )
                    minutes = int(time_spent.total_seconds() / 60)

                    if minutes > 0:
                        # Check if voice XP is enabled
                        voice_xp_enabled = await self.bot.db_manager.get_setting("xp_voice_enabled", member.guild.id)
                        if voice_xp_enabled == "false":
                            del self.bot.voice_time[member.id]
                            return
                        
                        # Get XP amount from database or use default
                        xp_per_minute_str = await self.bot.db_manager.get_setting("xp_per_voice_minute", member.guild.id)
                        xp_per_minute = int(xp_per_minute_str) if xp_per_minute_str else XP_PER_VOICE_MINUTE
                        
                        if xp_per_minute <= 0:
                            del self.bot.voice_time[member.id]
                            return
                        
                        xp_gained = minutes * xp_per_minute
                        # Award voice XP
                        new_xp, new_level, leveled_up = await self.bot.db_manager.update_user_xp(member.id, xp_gained, member.guild.id)
                        
                        # Check for level-up
                        if leveled_up:
                            await self._check_level_up(member)

                    del self.bot.voice_time[member.id]

        except Exception as e:
            self.logger.error(f"Error in voice XP tracking: {e}")

    async def _check_level_up(self, user):
        """Check if user leveled up and assign roles if needed."""
        self.logger.debug(f"_check_level_up called for {user.name}")
        self.logger.info(f"[LEVEL ROLE] _check_level_up called for user {user.name} (ID: {user.id})")

        try:
            # Get user's current level
            current_level = await self.bot.db_manager.get_user_level(user.id, user.guild.id)
            self.logger.info(f"[LEVEL ROLE DEBUG] User {user.name} is level {current_level}")

            # Check if we already sent a level-up message for this level
            level_key = f"{user.id}_{current_level}"
            if level_key in self.level_up_sent:
                self.logger.info(f"[LEVEL ROLE DEBUG] Already sent level-up message for {user.name} level {current_level}, skipping")
            else:
                # Mark this level as sent
                self.level_up_sent[level_key] = True
                
                # Send level-up message to XP channel
                xp_channel_id = await self.bot.db_manager.get_setting("xp_channel", user.guild.id)
                levelup_message = await self.bot.db_manager.get_setting("xp_levelup_message", user.guild.id)
                
                self.logger.info(f"[LEVEL ROLE DEBUG] XP channel ID: {xp_channel_id}")
                self.logger.info(f"[LEVEL ROLE DEBUG] Level-up message template: {levelup_message}")

                if xp_channel_id:
                    channel = user.guild.get_channel(int(xp_channel_id))
                    self.logger.info(f"[LEVEL ROLE DEBUG] Channel object: {channel}")
                    if channel:
                        # Format the message
                        msg = levelup_message or "🎉 {member} reached level {level}!"
                        msg = msg.replace("{member}", user.mention)
                        msg = msg.replace("{level}", str(current_level))

                        try:
                            await channel.send(msg)
                            self.logger.info(f"Sent level-up message for {user.name} reaching level {current_level}")
                        except Exception as e:
                            self.logger.error(f"Failed to send level-up message: {e}")

            # Check for level roles (always check, even if message was already sent)
            conn = await self.bot.db_manager.get_connection()
            cursor = await conn.execute(
                "SELECT level, role_id FROM level_roles WHERE guild_id = ?",
                (user.guild.id,),
            )
            rows = await cursor.fetchall()
            self.logger.info(f"[LEVEL ROLE DEBUG] Found {len(rows)} level roles configured for guild {user.guild.id}")

            for level, role_id in rows:
                self.logger.info(f"[LEVEL ROLE DEBUG] Checking level {level} role (ID: {role_id})")
                # If user reached this level, assign the role
                if current_level >= level:
                    role = user.guild.get_role(int(role_id))
                    self.logger.info(f"[LEVEL ROLE DEBUG] Role object: {role}")
                    if role and role not in user.roles:
                        self.logger.info(f"[LEVEL ROLE DEBUG] Attempting to assign role {role.name} to {user.name}")
                        await user.add_roles(role, reason=f"Reached level {level}")
                        self.logger.info(
                            f"Assigned role {role.name} to {user.name} for reaching level {level}"
                        )
                    elif role in user.roles:
                        self.logger.info(f"[LEVEL ROLE DEBUG] User already has role {role.name}")
                    else:
                        self.logger.warning(f"[LEVEL ROLE DEBUG] Role not found or is None")

        except Exception as e:
            self.logger.error(f"Error checking level up: {e}")

@commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Clean up XP and checkin data when a user leaves the server."""
        try:
            # Clean up all user data for this guild
            await self.bot.db_manager.cleanup_user_data(member.id, member.guild.id)
            self.logger.info(f"Cleaned up XP data for {member.name} ({member.id}) who left guild {member.guild.id}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up XP data for user {member.id} leaving guild {member.guild.id}: {e}")


async def setup(bot: commands.Bot):
    """Setup the XP cog."""
    xp_cog = XP(bot)
    await bot.add_cog(xp_cog)
    xp_group = XPGroup(xp_cog)
    xp_cog._xp_group = xp_group  # Store reference for cleanup
    bot.tree.add_command(xp_group)


def calculate_level(xp: int) -> int:
    """Calculate level from total XP."""
    if xp < 0:
        return 1

    level = 1
    # Sort levels in descending order and find the highest level we qualify for
    for lvl in sorted(XP_TABLE.keys(), reverse=True):
        if xp >= XP_TABLE[lvl]:
            level = lvl
            break

    return level
