"""
Verify Cog for MalaBoT
Parent slash command: /verify
Subcommands: submit, review
"""

import typing
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, Select, TextInput, View

from config.constants import COLORS
from utils.helpers import create_embed, safe_send_message
from utils.logger import log_system

# Platform options for dropdown
PLATFORM_OPTIONS = [
    discord.SelectOption(label="Xbox", value="xbox", emoji="🎮"),
    discord.SelectOption(label="PlayStation", value="playstation", emoji="🎮"),
    discord.SelectOption(label="Steam", value="steam", emoji="💻"),
]


class ActivisionIDModal(Modal, title="Submit Verification"):
    activision_id = TextInput(
        label="Activision ID",
        placeholder="Enter your Activision ID (e.g., Username#1234567)",
        required=True,
        max_length=100,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=create_embed(
                "Upload Screenshot",
                f"**Activision ID:** `{self.activision_id.value}`\n\n"
                "Please upload your **Warzone Combat Record screenshot** in your next message.\n"
                "The screenshot should clearly show your Activision ID and stats.",
                COLORS["info"],
            ),
            ephemeral=True,
        )

        # Store the activision_id temporarily with channel context
        self.bot.pending_verifications[interaction.user.id] = {
            "activision_id": self.activision_id.value,
            "timestamp": datetime.now(),
            "channel_id": interaction.channel_id,
        }


class PlatformSelect(Select):
    def __init__(
        self,
        activision_id: str,
        screenshot_url: str,
        user_id: int,
        screenshot_bytes=None,
        screenshot_filename=None,
    ):
        super().__init__(
            placeholder="Select your gaming platform...",
            min_values=1,
            max_values=1,
            options=PLATFORM_OPTIONS,
        )
        self.activision_id = activision_id
        self.screenshot_url = screenshot_url
        self.user_id = user_id
        self.screenshot_bytes = screenshot_bytes
        self.screenshot_filename = screenshot_filename

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

            # Delete the platform selection message to clean up the channel
            try:
                await interaction.message.delete()
            except:
                pass

            # Send a brief public confirmation that auto-deletes
            confirmation_msg = await interaction.channel.send(
                embed=create_embed(
                    "✅ Verification Submitted",
                    f"<@{self.user_id}>'s verification has been submitted for review!",
                    COLORS["success"],
                )
            )

            # Also send ephemeral confirmation to user
            await interaction.response.send_message(
                embed=create_embed(
                    "Verification Submitted ✅",
                    "Your verification has been sent for mod review. You'll be notified once it's approved or rejected.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )

            # Delete the confirmation message after 5 seconds
            import asyncio

            await asyncio.sleep(5)
            try:
                await confirmation_msg.delete()
            except:
                pass

            log_system(
                f"[VERIFY] User {self.user_id} submitted verification for {self.activision_id} on {platform}"
            )

            guild_id = interaction.guild.id if interaction.guild else None
            review_channel_id = await db.get_setting("verify_channel", guild_id)
            review_channel = (
                bot.get_channel(int(review_channel_id)) if review_channel_id else None
            )

            if review_channel:
                # Debug logging
                log_system(
                    f"[VERIFY_DEBUG] Has screenshot bytes: {self.screenshot_bytes is not None}"
                )

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

                embed.set_footer(text=f"User ID: {self.user_id}")

                # Send with screenshot file attachment if available
                if self.screenshot_bytes and self.screenshot_filename:
                    import io

                    file = discord.File(
                        io.BytesIO(self.screenshot_bytes),
                        filename=self.screenshot_filename,
                    )
                    embed.set_image(url=f"attachment://{self.screenshot_filename}")
                    await review_channel.send(embed=embed, file=file)
                else:
                    log_system(
                        f"[VERIFY_WARNING] No screenshot data for user {self.user_id}",
                        level="warning",
                    )
                    await review_channel.send(embed=embed)

            await db.log_event(
                category="VERIFY",
                action="SUBMIT",
                user_id=self.user_id,
                details=f"{self.activision_id} ({platform})",
            )

            # Clean up pending verification
            if self.user_id in bot.pending_verifications:
                del bot.pending_verifications[self.user_id]

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
    def __init__(
        self,
        activision_id: str,
        screenshot_url: str,
        user_id: int,
        screenshot_bytes=None,
        screenshot_filename=None,
    ):
        super().__init__(timeout=180)
        self.add_item(
            PlatformSelect(
                activision_id,
                screenshot_url,
                user_id,
                screenshot_bytes,
                screenshot_filename,
            )
        )


class VerifyGroup(app_commands.Group):
    """Verify command group"""

    def __init__(self, cog):
        super().__init__(name="verify", description="Warzone verification system")
        self.cog = cog

    @app_commands.command(
        name="activision",
        description="Submit your Warzone verification with Activision ID",
    )
    async def activision(self, interaction: discord.Interaction):
        """Submit verification - opens modal for Activision ID, then asks for screenshot."""
        modal = ActivisionIDModal(self.cog.bot)
        await interaction.response.send_modal(modal)

    @app_commands.command(
        name="review", description="Review a pending verification (mod only)"
    )
    @app_commands.describe(
        user="The user to review",
        decision="verified, cheater, or unverified",
        notes="Optional notes about the decision (reason for decision)",
    )
    @app_commands.choices(
        decision=[
            app_commands.Choice(name="Verified", value="verified"),
            app_commands.Choice(name="Cheater", value="cheater"),
            app_commands.Choice(name="Unverified", value="unverified"),
        ]
    )
    async def review(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        decision: app_commands.Choice[str],
        notes: typing.Optional[str] = None,
    ):
        try:
            # Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=True, thinking=True)

            # Check staff permission (uses general mod role)
            from utils.helpers import check_mod_permission

            if not await check_mod_permission(interaction, self.cog.db):
                return

            guild_id = interaction.guild.id
            decision_value = decision.value

            # Debug logging
            log_system(
                f"[VERIFY_REVIEW_DEBUG] Notes received: '{notes}' (type: {type(notes)})"
            )

            if decision_value not in ["verified", "cheater", "unverified"]:
                await safe_send_message(
                    interaction,
                    content="Use `verified`, `cheater`, or `unverified`.",
                    ephemeral=True,
                )
                return

            conn = await self.cog.db.get_connection()
            await conn.execute(
                "UPDATE verifications SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP, notes = ? WHERE discord_id = ?",
                (decision_value, interaction.user.id, notes, user.id),
            )
            await conn.commit()

            guild = interaction.guild
            member = guild.get_member(user.id)
            result_text = ""

            if decision_value == "verified" and member:
                # Get verified role from settings
                verified_role_id = await self.cog.db.get_setting(
                    "verify_role", guild_id
                )

                if verified_role_id:
                    verified_role = guild.get_role(int(verified_role_id))
                    if verified_role:
                        await member.add_roles(verified_role)
                        result_text = f"✅ Verified {member.mention} and assigned {verified_role.mention} role."
                    else:
                        result_text = f"✅ Verified {member.mention} but verified role not found. Please run `/setup` and select Verification System to configure."
                else:
                    result_text = f"✅ Verified {member.mention} but no verified role configured. Please run `/setup` and select Verification System to configure."

            elif decision_value == "unverified" and member:
                result_text = (
                    f"❌ Marked {user.mention} as unverified. They remain unverified."
                )

            elif decision_value == "cheater" and member:
                print(f"DEBUG: Processing cheater for {member.name}")
                # Get cheater role and channel from settings
                cheater_role_id = await self.cog.db.get_setting(
                    "cheater_role", guild_id
                )
                print(f"DEBUG: Cheater role ID: {cheater_role_id}")
                cheater_channel_id = await self.cog.db.get_setting(
                    "cheater_jail_channel", guild_id
                )

                if cheater_role_id and cheater_channel_id:
                    cheater_role = guild.get_role(int(cheater_role_id))
                    cheater_channel = guild.get_channel(int(cheater_channel_id))

                    if cheater_role and cheater_channel:
                        try:
                            # Lock member to prevent role connections from interfering
                            bot = interaction.client
                            bot.processing_members.add(member.id)

                            try:
                                # Add cheater role FIRST
                                await member.add_roles(
                                    cheater_role,
                                    reason=f"Marked as cheater by {interaction.user}",
                                )

                                # Then remove all other roles except @everyone and cheater
                                roles_to_remove = [
                                    role
                                    for role in member.roles
                                    if role != guild.default_role
                                    and role != cheater_role
                                ]
                                if roles_to_remove:
                                    await member.remove_roles(
                                        *roles_to_remove,
                                        reason=f"Marked as cheater by {interaction.user}",
                                    )

                                # Send notification to cheater jail
                                jail_embed = discord.Embed(
                                    title="🚨 New Arrival",
                                    description=(
                                        f"{member.mention} has been sent to cheater jail.\n\n"
                                        f"**Reason:** Confirmed cheater during verification\n"
                                        f"**Reviewed by:** {interaction.user.mention}\n"
                                        f"**Notes:** {notes or 'None provided'}\n\n"
                                        f"You can submit ONE appeal using `/appeal`"
                                    ),
                                    color=COLORS["error"],
                                )
                                await cheater_channel.send(
                                    content=f"{member.mention}", embed=jail_embed
                                )

                                result_text = f"🔒 Sent {member.mention} to cheater jail ({cheater_channel.mention}) with {cheater_role.mention} role."
                            finally:
                                # Always release the lock
                                bot.processing_members.discard(member.id)

                        except discord.Forbidden:
                            result_text = f"❌ Failed to assign cheater role to {member.mention}. Missing permissions."
                    else:
                        result_text = "❌ Cheater role or channel not found. Please configure in `/setup` → Verification System"
                else:
                    result_text = "❌ Cheater jail system not configured. Please run `/setup` → Verification System to set up cheater role and channel."

            # Send ephemeral confirmation to moderator
            await safe_send_message(interaction, content=result_text, ephemeral=True)

            # Send public message to the channel
            try:
                public_embed = discord.Embed(
                    title=(
                        "✅ Verification Reviewed"
                        if decision_value == "verified"
                        else "❌ Verification Decision"
                    ),
                    description=(
                        f"**User:** {user.mention}\n"
                        f"**Decision:** {decision_value.upper()}\n"
                        f"**Reviewed by:** {interaction.user.mention}\n"
                        f"**Notes:** {notes or 'None provided'}"
                    ),
                    color=(
                        COLORS["success"]
                        if decision_value == "verified"
                        else COLORS["error"]
                    ),
                )
                await interaction.channel.send(embed=public_embed)
            except Exception as e:
                log_system(
                    f"Failed to send public verification message: {e}", level="error"
                )

            log_system(
                f"[VERIFY_REVIEW] {interaction.user} {decision_value.upper()} {user} ({notes or 'no notes'})"
            )
            await self.cog.db.log_event(
                category="VERIFY",
                action="REVIEW",
                user_id=user.id,
                target_id=interaction.user.id,
                details=f"{decision_value.upper()} - {notes or 'No notes'}",
            )

            # DM user about decision (except for cheaters)
            if decision_value != "cheater":
                try:
                    dm_embed = create_embed(
                        "Verification Update",
                        f"Your verification was **{decision_value.upper()}**.\nNotes: {notes or 'None provided.'}",
                        (
                            COLORS["info"]
                            if decision_value == "verified"
                            else COLORS["error"]
                        ),
                    )
                    await user.send(embed=dm_embed)
                except discord.Forbidden:
                    log_system(
                        f"Could not DM {user} about verification result.",
                        level="warning",
                    )

        except Exception as e:
            log_system(f"Verification review error: {e}", level="error")
            await safe_send_message(
                interaction,
                content="An error occurred while processing review.",
                ephemeral=True,
            )


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager
        # Store pending verifications temporarily
        if not hasattr(bot, "pending_verifications"):
            bot.pending_verifications = {}

    async def cog_unload(self):
        """Remove the command group when cog is unloaded"""
        if hasattr(self, "_verify_group"):
            self.bot.tree.remove_command(self._verify_group.name)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Listen for role changes and handle cheater role assignment"""
        # Skip if member is being processed by another system
        if after.id in self.bot.processing_members:
            return

        # Check if any roles were added
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        added_roles = after_roles - before_roles

        if not added_roles:
            return

        guild_id = after.guild.id
        cheater_role_id = await self.db.get_setting("cheater_role", guild_id)

        if not cheater_role_id:
            return

        cheater_role = after.guild.get_role(int(cheater_role_id))
        if not cheater_role:
            return

        # Check if user currently has cheater role (not just if it was added)
        if cheater_role in after.roles:
            # User has cheater role - remove ANY other roles that were added
            try:
                # Lock member to prevent role connections from interfering
                self.bot.processing_members.add(after.id)

                try:
                    roles_to_remove = [
                        role
                        for role in after.roles
                        if role != after.guild.default_role and role != cheater_role
                    ]
                    if roles_to_remove:
                        await after.remove_roles(
                            *roles_to_remove,
                            reason="Cheater role active - removing all other roles",
                        )
                        log_system(
                            f"[CHEATER_ROLE] Removed {len(roles_to_remove)} roles from {after.name} (cheater role protection)"
                        )
                finally:
                    # Always release the lock
                    self.bot.processing_members.discard(after.id)

            except discord.Forbidden:
                log_system(
                    f"[CHEATER_ROLE] Failed to remove roles from {after.name} - missing permissions",
                    level="error",
                )
            except Exception as e:
                log_system(
                    f"[CHEATER_ROLE] Error removing roles from {after.name}: {e}",
                    level="error",
                )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listen for screenshot uploads from users with pending verifications."""
        if message.author.bot:
            return

        user_id = message.author.id
        if user_id not in self.bot.pending_verifications:
            return

        # Get pending verification data
        pending = self.bot.pending_verifications[user_id]

        # CRITICAL: Only process if message is in the same channel where verification was started
        if message.channel.id != pending.get("channel_id"):
            if not message.attachments:
                   return

        activision_id = pending["activision_id"]
        screenshot = message.attachments[0]

        # Check if attachment is an image
        if not any(
            screenshot.filename.lower().endswith(ext)
            for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
        ):
            await message.reply(
                embed=create_embed(
                    "Invalid File Type",
                    "Please upload an image file (PNG, JPG, JPEG, GIF, or WEBP).",
                    COLORS["error"],
                ),
                delete_after=10,
            )
            return

        # Download screenshot bytes for later re-upload
        screenshot_bytes = await screenshot.read()

        # Delete the screenshot message BEFORE sending reply
        try:
            await message.delete()
        except Exception as e:
            log_system(f"Failed to delete screenshot message: {e}", level="warning")

        # Send platform selection to the channel (not as reply since original message is deleted)
        view = PlatformView(
            activision_id,
            screenshot.url,
            user_id,
            screenshot_bytes,
            screenshot.filename,
        )
        await message.channel.send(
            content=message.author.mention,
            embed=create_embed(
                "Select Your Platform",
                f"**Activision ID:** `{activision_id}`\n\nPlease select your gaming platform from the dropdown below:",
                COLORS["info"],
            ),
            view=view,
        )


async def setup(bot: commands.Bot):
    verify_cog = Verify(bot)
    await bot.add_cog(verify_cog)
    verify_group = VerifyGroup(verify_cog)
    verify_cog._verify_group = verify_group  # Store reference for cleanup
    bot.tree.add_command(verify_group)
