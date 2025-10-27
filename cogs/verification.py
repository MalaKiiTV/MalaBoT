"""
Verification Cog for MalaBoT
Handles Warzone player verification submissions and staff reviews.
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from utils.helpers import create_embed, safe_send_message
from utils.logger import log_system
from config.constants import COLORS

# === CONFIG ===
VERIFIED_ROLE_NAME = "Verified"                      # Role assigned after approval


class Verification(commands.Cog):
    """Cog handling Warzone player verification workflow."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager

    # ============================================================
    # USER COMMAND — SUBMIT VERIFICATION
    # ============================================================
    @app_commands.command(name="verify", description="Submit your Warzone verification screenshot.")
    async def verify(self, interaction: discord.Interaction, activision_id: str, platform: str):
        """
        Allows a user to submit their verification screenshot and Activision ID.
        """
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)

            # === Ensure screenshot attached ===
            if not interaction.attachments:
                await safe_send_message(
                    interaction,
                    embed=create_embed(
                        "Missing Screenshot",
                        "Please attach your **Warzone Combat Record screenshot** showing your Activision ID and stats.",
                        COLORS["error"],
                    ),
                    ephemeral=True,
                )
                return

            screenshot = interaction.attachments[0]

            # === Insert submission into DB ===
            conn = await self.db.get_connection()
            await conn.execute(
                """
                INSERT INTO verifications (discord_id, activision_id, platform, screenshot_url)
                VALUES (?, ?, ?, ?)
                """,
                (interaction.user.id, activision_id, platform, screenshot.url),
            )
            await conn.commit()

            # === Confirmation to user ===
            await safe_send_message(
                interaction,
                embed=create_embed(
                    "Verification Submitted ✅",
                    "Your verification has been sent for staff review. "
                    "You'll be notified once it's approved or rejected.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )

            # === Log and notify staff ===
            log_system(f"[VERIFY] {interaction.user} submitted verification for {activision_id}")

            # === Get review channel from DB settings ===
            guild_id = interaction.guild.id if interaction.guild else None
            review_channel_id = await self.db.get_setting(f"verify_channel_{guild_id}")
            review_channel = self.bot.get_channel(int(review_channel_id)) if review_channel_id else None

            # If no channel configured, inform user and exit
            if not review_channel:
                await safe_send_message(
                    interaction,
                    embed=create_embed(
                        "Setup Required",
                        "No review channel is configured yet. "
                        "An administrator must run `/verify_setup` first to choose one.",
                        COLORS["warning"],
                    ),
                    ephemeral=True,
                )
                return

            # === Send submission embed to review channel ===
            embed = discord.Embed(
                title="📸 New Verification Submission",
                description=(
                    f"**User:** {interaction.user.mention}\n"
                    f"**Activision ID:** `{activision_id}`\n"
                    f"**Platform:** `{platform}`\n"
                    f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
                color=COLORS["info"],
            )
            embed.set_image(url=screenshot.url)
            embed.set_footer(text=f"User ID: {interaction.user.id}")
            await review_channel.send(embed=embed)

            await self.db.log_event(
                category="VERIFY",
                action="SUBMIT",
                user_id=interaction.user.id,
                details=f"{activision_id} ({platform})",
            )

        except Exception as e:
            log_system(f"Verification submission failed: {e}", level="error")
            await safe_send_message(
                interaction,
                embed=create_embed(
                    "Error",
                    "Something went wrong submitting your verification. Please try again later.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )

    # ============================================================
    # STAFF COMMAND — REVIEW VERIFICATION
    # ============================================================
    @app_commands.command(name="verify_review", description="Review a pending verification (staff only).")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def verify_review(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        decision: str,
        notes: str = None,
    ):
        """
        Allows moderators/admins to approve or reject a verification.
        """
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            decision = decision.lower()

            if decision not in ["approve", "reject"]:
                await safe_send_message(interaction, content="Use either `approve` or `reject`.", ephemeral=True)
                return

            conn = await self.db.get_connection()
            await conn.execute(
                """
                UPDATE verifications
                SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, notes = ?
                WHERE discord_id = ?
                """,
                (decision, interaction.user.id, notes, user.id),
            )
            await conn.commit()

            guild = interaction.guild
            member = guild.get_member(user.id)
            result_text = ""

            # === Handle approval ===
            if decision == "approve" and member:
                verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
                if not verified_role:
                    verified_role = await guild.create_role(name=VERIFIED_ROLE_NAME, color=discord.Color.green())
                await member.add_roles(verified_role)
                result_text = f"✅ Approved {member.mention} and assigned **{VERIFIED_ROLE_NAME}** role."
            else:
                result_text = f"❌ Rejected {user.mention}."

            await safe_send_message(interaction, content=result_text, ephemeral=True)

            # === Log event ===
            log_system(f"[VERIFY_REVIEW] {interaction.user} {decision.upper()} {user} ({notes or 'no notes'})")
            await self.db.log_event(
                category="VERIFY",
                action="REVIEW",
                user_id=user.id,
                target_id=interaction.user.id,
                details=f"{decision.upper()} - {notes or 'No notes'}",
            )

            # === Notify the user ===
            try:
                dm_embed = create_embed(
                    "Verification Update",
                    f"Your verification was **{decision.upper()}**.\nNotes: {notes or 'None provided.'}",
                    COLORS["info"],
                )
                await user.send(embed=dm_embed)
            except discord.Forbidden:
                log_system(f"Could not DM {user} about verification result.", level="warning")

        except Exception as e:
            log_system(f"Verification review error: {e}", level="error")
            await safe_send_message(interaction, content="An error occurred while processing review.", ephemeral=True)
    # ============================================================
    # ADMIN COMMAND — SET REVIEW CHANNEL (Server Config)
    # ============================================================
    @app_commands.command(name="verify_setup", description="Set up the verification review channel (admin only).")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Allows server admins to set the review channel dynamically per guild.
        """
        try:
            await self.db.set_setting(f"verify_channel_{interaction.guild.id}", channel.id)
            await self.db.log_event(
                category="VERIFY",
                action="SETUP_CHANNEL",
                user_id=interaction.user.id,
                details=f"Set review channel to #{channel.name}",
                guild_id=interaction.guild.id,
            )
            await safe_send_message(
                interaction,
                embed=create_embed(
                    "Verification Setup Complete",
                    f"✅ Review channel set to {channel.mention}.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
            log_system(f"[VERIFY_SETUP] {interaction.guild.name} -> {channel.name}")

        except Exception as e:
            log_system(f"verify_setup error: {e}", level="error")
            await safe_send_message(
                interaction,
                embed=create_embed(
                    "Error",
                    "Unable to set review channel. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )

    # ============================================================
    # COG LOADER
    # ============================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
