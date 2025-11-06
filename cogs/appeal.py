"""
Appeal Cog for MalaBoT
Allows cheaters in jail to submit ONE appeal
Command: /appeal (submit and review)
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
from typing import Optional

from config.constants import COLORS
from utils.helpers import create_embed, safe_send_message
from utils.logger import log_system


class AppealGroup(app_commands.Group):
    """Appeal command group"""

    def __init__(self, cog):
        super().__init__(name="appeal", description="Appeal system for cheater jail")
        self.cog = cog

    @app_commands.command(name="submit", description="Submit an appeal (one-time only)")
    async def submit(self, interaction: discord.Interaction):
        """Submit an appeal - can only be used once"""
        guild_id = interaction.guild and interaction.guild and interaction.guild.id

        # Get settings in parallel to reduce latency
        import asyncio

        cheater_role_id, cheater_channel_id = await asyncio.gather(
            self.cog.db.get_setting("cheater_role", guild_id),
            self.cog.db.get_setting("cheater_channel", guild_id),
        )

        # Check if user is in cheater jail
        if cheater_role_id:
            cheater_role = interaction.guild and interaction.guild and interaction.guild.get_role(int(cheater_role_id))
            if cheater_role and cheater_role not in interaction.user.roles:
                await interaction.response.send_message(
                    embed=create_embed(
                        "Not in Cheater Jail",
                        "❌ You can only submit an appeal if you're in cheater jail.",
                        COLORS["error"],
                    ),
                    ephemeral=True,
                )
                return

        # Check if in cheater jail channel
        if cheater_channel_id and interaction.channel_id != int(cheater_channel_id):
            cheater_channel = interaction.guild and interaction.guild and interaction.guild.get_channel(int(cheater_channel_id))
            await interaction.response.send_message(
                embed=create_embed(
                    "Wrong Channel",
                    f"❌ You can only submit appeals in {cheater_channel.mention}",
                    COLORS["error"],
                ),
                ephemeral=True,
            )
            return

        modal = AppealModal(self.cog.db, guild_id)
        await interaction.response.send_modal(modal)

    @app_commands.command(
        name="appeal-review", description="Review a user's appeal (mod only)"
    )
    @app_commands.describe(
        user="The user whose appeal to review",
        decision="approve or deny",
        reason="Reason for the decision",
    )
    @app_commands.choices(
        decision=[
            app_commands.Choice(name="Approve", value="approve"),
            app_commands.Choice(name="Deny", value="deny"),
        ]
    )
    async def review(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        decision: app_commands.Choice[str],
        reason: str = None,
    ):
        """Review an appeal"""
        try:
            # Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=True, thinking=True)

            # Check staff permission
            from utils.helpers import check_staff_permission

            if not await check_staff_permission(interaction, self.cog.db):
                return

            guild_id = interaction.guild and interaction.guild and interaction.guild.id

            # Check if appeal exists
            conn = await self.cog.db.get_connection()
            cursor = await conn.execute(
                "SELECT appeal_text, status FROM appeals WHERE user_id = ? AND guild_id = ?",
                (user.id, guild_id),
            )
            appeal_data = await cursor.fetchone()

            if not appeal_data:
                await safe_send_message(
                    interaction,
                    content=f"❌ No appeal found for {user.mention}",
                    ephemeral=True,
                )
                return

            appeal_text, current_status = appeal_data

            if current_status != "pending":
                await safe_send_message(
                    interaction,
                    content=f"❌ This appeal has already been {current_status}",
                    ephemeral=True,
                )
                return

            decision_value = decision.value
            member = interaction.guild and interaction.guild and interaction.guild.get_member(user.id)

            if decision_value == "approve" and member:
                # Remove cheater role
                cheater_role_id = await self.cog.db.get_setting(
                    "cheater_role", guild_id
                )
                if cheater_role_id:
                    cheater_role = interaction.guild and interaction.guild and interaction.guild.get_role(int(cheater_role_id))
                    if cheater_role and cheater_role in member.roles:
                        await member.remove_roles(
                            cheater_role,
                            reason=f"Appeal approved by {interaction.user}",
                        )

                # Update appeal status
                await conn.execute(
                    "UPDATE appeals SET status = 'approved', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, review_notes = ? WHERE user_id = ? AND guild_id = ?",
                    (interaction.user.id, reason, user.id, guild_id),
                )
                await conn.commit()

                result_text = (
                    f"✅ Approved {member.mention}'s appeal and removed cheater role."
                )

                # DM user
                try:
                    dm_embed = create_embed(
                        "Appeal Approved ✅",
                        f"Your appeal has been **APPROVED**.\n\n"
                        f"**Reason:** {reason or 'None provided'}\n\n"
                        f"You have been released from cheater jail. Welcome back!",
                        COLORS["success"],
                    )
                    if user and hasattr(user, "send"): await user.send(embed=dm_embed)
                except discord.Forbidden:
                    log_system(
                        f"Could not DM {user} about appeal approval.", level="warning"
                    )

            elif decision_value == "deny":
                # Update appeal status
                await conn.execute(
                    "UPDATE appeals SET status = 'denied', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, review_notes = ? WHERE user_id = ? AND guild_id = ?",
                    (interaction.user.id, reason, user.id, guild_id),
                )
                await conn.commit()

                result_text = (
                    f"❌ Denied {user.mention}'s appeal. They remain in cheater jail."
                )

                # DM user
                try:
                    dm_embed = create_embed(
                        "Appeal Denied ❌",
                        f"Your appeal has been **DENIED**.\n\n"
                        f"**Reason:** {reason or 'None provided'}\n\n"
                        f"You will remain in cheater jail.",
                        COLORS["error"],
                    )
                    if user and hasattr(user, "send"): await user.send(embed=dm_embed)
                except discord.Forbidden:
                    log_system(
                        f"Could not DM {user} about appeal denial.", level="warning"
                    )

            await safe_send_message(interaction, content=result_text, ephemeral=True)

            log_system(
                f"[APPEAL_REVIEW] {interaction.user} {decision_value.upper()} appeal from {user}"
            )
            await self.cog.db.log_event(
                category="APPEAL",
                action="REVIEW",
                user_id=user.id,
                target_id=interaction.user.id,
                guild_id=guild_id,
                details=f"{decision_value.upper()} - {reason or 'No reason'}",
            )

        except Exception as e:
            log_system(f"Appeal review error: {e}", level="error")
            await safe_send_message(
                interaction,
                content="An error occurred while processing the appeal review.",
                ephemeral=True,
            )


class AppealModal(Modal, title="Submit Appeal"):
    """Modal for submitting an appeal"""

    appeal_text = TextInput(
        label="Your Appeal",
        placeholder="Explain why you believe you were wrongly marked as a cheater...",
        required=True,
        max_length=1000,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, db_manager, guild_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = interaction.user.id

            # Check if user already submitted a PENDING appeal for this jail session
            conn = await self.db.get_connection()
            cursor = await conn.execute(
                "SELECT COUNT(*) FROM appeals WHERE user_id = ? AND guild_id = ? AND status = 'pending'",
                (user_id, self.guild_id),
            )
            count = (await cursor.fetchone())[0]

            if count > 0:
                await interaction.response.send_message(
                    embed=create_embed(
                        "Appeal Already Submitted",
                        "❌ You have already submitted an appeal. You can only appeal once per jail session.\n\n"
                        "Please wait for staff to review your appeal.",
                        COLORS["error"],
                    ),
                    ephemeral=True,
                )
                return

            # Store appeal in database
            await conn.execute(
                "INSERT INTO appeals (user_id, guild_id, appeal_text, status, submitted_at) VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)",
                (user_id, self.guild_id, self.appeal_text.value),
            )
            await conn.commit()

            await interaction.response.send_message(
                embed=create_embed(
                    "Appeal Submitted ✅",
                    "Your appeal has been submitted to staff for review.\n\n"
                    "You will be notified once a decision is made.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )

            # Notify staff in review channel
            review_channel_id = await self.db.get_setting(
                "verify_channel", self.guild_id
            )
            if review_channel_id:
                review_channel = interaction.guild and interaction.guild and interaction.guild.get_channel(int(review_channel_id))
                if review_channel:
                    embed = discord.Embed(
                        title="📝 New Appeal Submitted",
                        description=(
                            f"**User:** {interaction.user.mention}\n"
                            f"**User ID:** `{user_id}`\n"
                            f"**Submitted:** {discord.utils.format_dt(discord.utils.utcnow(), 'F')}\n\n"
                            f"**Appeal:**\n{self.appeal_text.value}"
                        ),
                        color=COLORS["info"],
                    )
                    embed.set_footer(
                        text=f"Use /appeal review @{interaction.user.name} <approve/deny> [reason]"
                    )
                    if review_channel and hasattr(review_channel, "send"): await review_channel.send(embed=embed)

            log_system(
                f"[APPEAL] User {user_id} submitted appeal in guild {self.guild_id}"
            )
            await self.db.log_event(
                category="APPEAL",
                action="SUBMIT",
                user_id=user_id,
                guild_id=self.guild_id,
                details="Appeal submitted",
            )

        except Exception as e:
            log_system(f"Error submitting appeal: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to submit appeal. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class Appeal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager  # type: ignore  # type: ignore  # type: ignore
        self._appeal_group: Optional[AppealGroup] = None  # Store reference for cleanup

    async def cog_unload(self):
        """Remove the command group when cog is unloaded"""
        if hasattr(self, "_appeal_group"):
            self.bot.tree.remove_command(self._appeal_group.name)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Cancel pending appeals when a user leaves the server"""
        try:
            conn = await self.db.get_connection()

            # Update any pending appeals to 'cancelled' status
            await conn.execute(
                "UPDATE appeals SET status = 'cancelled', reviewed_at = CURRENT_TIMESTAMP WHERE user_id = ? AND guild_id = ? AND status = 'pending'",
                (member.id, member.guild.id),
            )
            await conn.commit()

            log_system(
                f"[APPEAL] Cancelled pending appeals for {member.name} (left server)"
            )
        except Exception as e:
            log_system(f"Error cancelling appeals on member leave: {e}", level="error")


async def setup(bot: commands.Bot):
    appeal_cog = Appeal(bot)
    await bot.add_cog(appeal_cog)
    appeal_group = AppealGroup(appeal_cog)
    appeal_cog._appeal_group = appeal_group  # Store reference for cleanup
    bot.tree.add_command(appeal_group)
