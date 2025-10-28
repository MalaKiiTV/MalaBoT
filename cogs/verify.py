"""
Verify Cog for MalaBoT
Parent slash command: /verify
Subcommands: submit, review, setup
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
from datetime import datetime
import aiohttp
import re

from utils.helpers import create_embed, safe_send_message
from utils.logger import log_system
from config.constants import COLORS

VERIFIED_ROLE_NAME = "Verified"

# Platform options for dropdown
PLATFORM_OPTIONS = [
    discord.SelectOption(label="Xbox", value="xbox", emoji="🎮"),
    discord.SelectOption(label="PlayStation", value="playstation", emoji="🎮"),
    discord.SelectOption(label="Steam", value="steam", emoji="💻"),
    discord.SelectOption(label="Battle.net", value="battlenet", emoji="⚔️"),
    discord.SelectOption(label="Other", value="other", emoji="❓"),
]


class PlatformSelect(Select):
    def __init__(self, activision_id: str, screenshot_url: str, user_id: int):
        super().__init__(
            placeholder="Select your gaming platform...",
            min_values=1,
            max_values=1,
            options=PLATFORM_OPTIONS,
        )
        self.activision_id = activision_id
        self.screenshot_url = screenshot_url
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        platform = self.values[0]
        
        try:
            bot = interaction.client
            db = bot.db_manager
            
            conn = await db.get_connection()
            await conn.execute(
                "INSERT INTO verifications (discord_id, activision_id, platform, screenshot_url) VALUES (?, ?, ?, ?)",
                (self.user_id, self.activision_id, platform, self.screenshot_url),
            )
            await conn.commit()

            await interaction.response.send_message(
                embed=create_embed(
                    "Verification Submitted ✅",
                    "Your verification has been sent for staff review. You'll be notified once it's approved or rejected.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )

            log_system(f"[VERIFY] User {self.user_id} submitted verification for {self.activision_id} on {platform}")

            guild_id = interaction.guild.id if interaction.guild else None
            review_channel_id = await db.get_setting(f"verify_channel_{guild_id}")
            review_channel = bot.get_channel(int(review_channel_id)) if review_channel_id else None

            if review_channel:
                embed = discord.Embed(
                    title="📸 New Verification Submission",
                    description=(
                        f"**User:** <@{self.user_id}>\n"
                        f"**Activision ID:** `{self.activision_id}`\n"
                        f"**Platform:** `{platform}`\n"
                        f"**Submitted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ),
                    color=COLORS["info"],
                )
                embed.set_image(url=self.screenshot_url)
                embed.set_footer(text=f"User ID: {self.user_id}")
                await review_channel.send(embed=embed)

            await db.log_event(
                category="VERIFY",
                action="SUBMIT",
                user_id=self.user_id,
                details=f"{self.activision_id} ({platform})",
            )

        except Exception as e:
            log_system(f"Platform selection callback error: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Something went wrong processing your selection. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class PlatformView(View):
    def __init__(self, activision_id: str, screenshot_url: str, user_id: int):
        super().__init__(timeout=180)
        self.add_item(PlatformSelect(activision_id, screenshot_url, user_id))


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager

    verify = app_commands.Group(name="verify", description="Warzone verification system.")

    # ============================================================
    # SUBCOMMAND — SUBMIT VERIFICATION
    # ============================================================
    @verify.command(name="submit", description="Submit your Warzone verification screenshot.")
    async def submit(self, interaction: discord.Interaction, activision_id: str):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)

            if not interaction.message or not interaction.message.attachments:
                # Check if there are attachments in the interaction itself
                if not hasattr(interaction, 'attachments') or not interaction.attachments:
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

            # Get screenshot from interaction
            screenshot = None
            if hasattr(interaction, 'attachments') and interaction.attachments:
                screenshot = interaction.attachments[0]
            elif interaction.message and interaction.message.attachments:
                screenshot = interaction.message.attachments[0]
            
            if not screenshot:
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

            # Send platform selection dropdown
            view = PlatformView(activision_id, screenshot.url, interaction.user.id)
            
            await interaction.followup.send(
                embed=create_embed(
                    "Select Your Platform",
                    f"**Activision ID:** `{activision_id}`\n\nPlease select your gaming platform from the dropdown below:",
                    COLORS["info"],
                ),
                view=view,
                ephemeral=True,
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
    # SUBCOMMAND — REVIEW VERIFICATION
    # ============================================================
    @verify.command(name="review", description="Review a pending verification (staff only).")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def review(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        decision: str,
        notes: str = None,
    ):
        try:
            await interaction.response.defer(ephemeral=True, thinking=True)
            decision = decision.lower()

            if decision not in ["approve", "reject"]:
                await safe_send_message(interaction, content="Use either `approve` or `reject`.", ephemeral=True)
                return

            conn = await self.db.get_connection()
            await conn.execute(
                "UPDATE verifications SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, notes = ? WHERE discord_id = ?",
                (decision, interaction.user.id, notes, user.id),
            )
            await conn.commit()

            guild = interaction.guild
            member = guild.get_member(user.id)
            result_text = ""

            if decision == "approve" and member:
                verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
                if not verified_role:
                    verified_role = await guild.create_role(name=VERIFIED_ROLE_NAME, color=discord.Color.green())
                await member.add_roles(verified_role)
                result_text = f"✅ Approved {member.mention} and assigned **{VERIFIED_ROLE_NAME}** role."
            else:
                result_text = f"❌ Rejected {user.mention}."

            await safe_send_message(interaction, content=result_text, ephemeral=True)

            log_system(f"[VERIFY_REVIEW] {interaction.user} {decision.upper()} {user} ({notes or 'no notes'})")
            await self.db.log_event(
                category="VERIFY",
                action="REVIEW",
                user_id=user.id,
                target_id=interaction.user.id,
                details=f"{decision.upper()} - {notes or 'No notes'}",
            )

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
    # SUBCOMMAND — SETUP VERIFICATION CHANNEL
    # ============================================================
    @verify.command(name="setup", description="Set up the verification review channel (admin only).")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))