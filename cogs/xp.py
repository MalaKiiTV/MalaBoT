"""
XP and leveling system cog for MalaBoT.
Handles user XP gains, level progression, and XP administration.
"""

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
            target = user or interaction.user

            # Get user stats from database
            xp = await self.cog.bot.db_manager.get_user_xp(target.id)
            level = await self.cog.bot.db_manager.get_user_level(target.id)

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

            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.cog.logger.error(f"Error in rank command: {e}")
            embed = embed_helper.error_embed(
                "Error", "Failed to fetch rank information."
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="leaderboard", description="Show server XP leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Show XP leaderboard."""
        try:
            # Get top users by XP for this guild only
            guild_member_ids = [member.id for member in interaction.guild.members]
            if not guild_member_ids:
                embed = create_embed(
                    title="\ud83c\udfc6 XP Leaderboard",
                    description="No guild members found!",
                    color=COLORS["warning"],
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            conn = await self.cog.bot.db_manager.get_connection()
            placeholders = ",".join(["?" for _ in guild_member_ids])
            cursor = await conn.execute(
                f"""SELECT user_id, xp
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
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            description = ""
            for i, (user_id, xp) in enumerate(rows, 1):
                # Calculate level from XP
                level = 1
                total_xp = xp
                for lvl, req_xp in enumerate(XP_TABLE):
                    if total_xp >= req_xp:
                        level = lvl + 1
                    else:
                        break
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

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.cog.logger.error(f"Error in leaderboard command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to fetch leaderboard.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="checkin", description="Claim your daily XP bonus")
    async def checkin(self, interaction: discord.Interaction):
        """Daily checkin for XP bonus."""
        try:
            user_id = interaction.user.id
            today = datetime.datetime.now().date()

            # Check last checkin
            conn = await self.cog.bot.db_manager.get_connection()
            cursor = await conn.execute(
                "SELECT last_checkin, checkin_streak FROM daily_checkins WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()

            if row:
                last_checkin = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
                if last_checkin == today:
                    embed = create_embed(
                        title="✅ Already Checked In",
                        description="You've already claimed your daily bonus today!",
                        color=COLORS["warning"],
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                # Calculate streak
                streak = row[1] if (today - last_checkin).days == 1 else 0
            else:
                streak = 0

            streak += 1

            # Calculate bonus with streak
            bonus = DAILY_CHECKIN_XP
            if streak > 1:
                bonus = int(bonus * (1 + (STREAK_BONUS_PERCENT * (streak - 1))))

            # Give XP
            await self.cog.bot.db_manager.update_user_xp(user_id, bonus)

            # Update checkin record
            await conn.execute(
                """INSERT OR REPLACE INTO daily_checkins (user_id, last_checkin, checkin_streak)
                   VALUES (?, ?, ?)""",
                (user_id, today.isoformat(), streak),
            )
            await conn.commit()

            embed = create_embed(
                title="✅ Daily Check-in Complete!",
                description=f"You've received **{bonus:,} XP**!\nCurrent streak: **{streak}** days",
                color=COLORS["success"],
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.cog.logger.error(f"Error in checkin command: {e}")
            embed = embed_helper.error_embed("Error", "Failed to process checkin.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
            await self.cog.bot.db_manager.update_user_xp(user.id, amount)
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
                    await self.cog.bot.db_manager.update_user_xp(member.id, amount)

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
            await self.cog.bot.db_manager.remove_user_xp(user.id, amount)
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
            await self.cog.bot.db_manager.set_user_xp(user.id, amount)
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
            await self.cog.bot.db_manager.set_user_xp(user.id, 0)
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


class XP(commands.Cog):
    """XP and leveling system."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger("xp")
        self.last_xp_time = {}  # Track last XP gain time per user

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

            # Award XP and get new level
            new_xp, new_level = await self.bot.db_manager.update_user_xp(
                user_id, XP_PER_MESSAGE
            )
            self.last_xp_time[user_id] = current_time

            # Level up is now handled automatically in update_user_xp
            # No separate level check needed

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

            # Award XP to message author (level up handled automatically)
            await self.bot.db_manager.update_user_xp(message.author.id, XP_PER_REACTION)
            # Level up is now handled automatically in update_user_xp

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
                        xp_gained = minutes * XP_PER_VOICE_MINUTE
                        # Award voice XP (level up handled automatically)
                        await self.bot.db_manager.update_user_xp(member.id, xp_gained)
                        # Level up is now handled automatically in update_user_xp

                    del self.bot.voice_time[member.id]

        except Exception as e:
            self.logger.error(f"Error in voice XP tracking: {e}")

    async def _check_level_up(self, user):
        """Check if user leveled up and assign roles if needed."""
        try:
            # Get user's current level
            current_level = await self.bot.db_manager.get_user_level(user.id)

            # Check for level roles
            conn = await self.bot.db_manager.get_connection()
            cursor = await conn.execute(
                "SELECT level, role_id FROM level_roles WHERE guild_id = ?",
                (user.guild.id,),
            )
            rows = await cursor.fetchall()

            for level, role_id in rows:
                # If user reached this level, assign the role
                if current_level >= level:
                    role = user.guild.get_role(int(role_id))
                    if role and role not in user.roles:
                        await user.add_roles(role, reason=f"Reached level {level}")
                        self.logger.info(
                            f"Assigned role {role.name} to {user.name} for reaching level {level}"
                        )

        except Exception as e:
            self.logger.error(f"Error checking level up: {e}")


async def setup(bot: commands.Bot):
    """Setup the XP cog."""
    xp_cog = XP(bot)
    await bot.add_cog(xp_cog)
    xp_group = XPGroup(xp_cog)
    xp_cog._xp_group = xp_group  # Store reference for cleanup
    bot.tree.add_command(xp_group)


def calculate_level(xp: int) -> int:
    """Calculate level from total XP."""
    level = 1
    for lvl, req_xp in enumerate(XP_TABLE):
        if xp >= req_xp:
            level = lvl + 1
        else:
            break
    return level
