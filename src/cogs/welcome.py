"""
Welcome system cog for MalaBoT.
Handles welcome messages for new members with customizable embeds.
"""

import asyncio

import discord
from discord.ext import commands

from src.config.constants import (
    COLORS,
    DEFAULT_GOODBYE_MESSAGE,
    DEFAULT_GOODBYE_TITLE,
    DEFAULT_WELCOME_MESSAGE,
    DEFAULT_WELCOME_TITLE,
)
from src.config.settings import settings
from src.utils.helpers import create_embed, embed_helper, is_admin, safe_send_message
from src.utils.logger import get_logger


class Welcome(commands.Cog):
    """Welcome system for new members."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger("welcome")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member joins."""
        try:
            if not self.bot.db_manager:
                return

            guild_id = member.guild.id

            # Assign "Onboarding" role to pending members
            if member.pending:
                onboarding_role_id = await self.bot.db_manager.get_setting("onboarding_role", guild_id)
                if onboarding_role_id:
                    onboarding_role = discord.utils.get(member.guild.roles, id=int(onboarding_role_id))
                    if onboarding_role:
                        try:
                            await member.add_roles(onboarding_role, reason="Member is completing onboarding")
                            self.logger.info(f"Assigned Onboarding role to {member.name}")
                        except discord.Forbidden:
                            self.logger.error(f"Missing permissions to assign Onboarding role to {member.name}")
                    else:
                        self.logger.warning(f"Onboarding role ID {onboarding_role_id} not found in guild")

            # Assign "Birthday Pending" role to all new members (if system enabled)
            birthday_pending_enabled = await self.bot.db_manager.get_setting("birthday_pending_enabled", guild_id)
            if birthday_pending_enabled == "true":
                birthday_pending_role_id = await self.bot.db_manager.get_setting("birthday_pending_role", guild_id)
                if birthday_pending_role_id:
                    birthday_pending_role = discord.utils.get(member.guild.roles, id=int(birthday_pending_role_id))
                    if birthday_pending_role:
                        try:
                            await member.add_roles(birthday_pending_role, reason="New member - birthday not set")
                            self.logger.info(f"Assigned Birthday Pending role to {member.name}")
                        except discord.Forbidden:
                            self.logger.error(f"Missing permissions to assign Birthday Pending role to {member.name}")
                    else:
                        self.logger.warning(f"Birthday Pending role ID {birthday_pending_role_id} not found in guild")

            # Check if welcome system is enabled
            guild_id = member.guild.id
            welcome_enabled = await self.bot.db_manager.get_setting("welcome_enabled", guild_id)
            
            # Skip if disabled (default to enabled if not set)
            if welcome_enabled == "false":
                return
            
            # Get welcome settings
            welcome_channel_id = await self.bot.db_manager.get_setting(
                "welcome_channel", guild_id
            )
            welcome_title = (
                await self.bot.db_manager.get_setting("welcome_title", guild_id)
                or DEFAULT_WELCOME_TITLE
            )
            welcome_message = (
                await self.bot.db_manager.get_setting("welcome_message", guild_id)
                or DEFAULT_WELCOME_MESSAGE
            )
            welcome_image = await self.bot.db_manager.get_setting(
                "welcome_image", guild_id
            )

            if not welcome_channel_id:
                return

            channel = self.bot.get_channel(int(welcome_channel_id))
            if not channel:
                self.logger.warning(f"Welcome channel {welcome_channel_id} not found")
                return

            # Format welcome message
            formatted_message = welcome_message.replace(
                "{member.mention}", member.mention
            )
            formatted_message = formatted_message.replace("{member.name}", member.name)
            formatted_message = formatted_message.replace(
                "{server.name}", member.guild.name
            )
            formatted_message = formatted_message.replace(
                "{member.count}", str(len(member.guild.members))
            )

            # Create welcome embed
            embed = create_embed(
                title=welcome_title.replace("{member.name}", member.name),
                description=formatted_message,
                color=COLORS["success"],
            )

            embed.set_thumbnail(
                url=(
                    member.display_avatar.url
                    if member.display_avatar
                    else member.default_avatar.url
                )
            )
            embed.set_footer(text=f"Member #{len(member.guild.members)}")

            # Add image if configured
            if welcome_image:
                embed.set_image(url=welcome_image)

            await safe_send_message(channel, embed=embed)

            self.logger.info(
                f"Sent welcome message for {member.name} in {member.guild.name}"
            )

        except Exception as e:
            self.logger.error(f"Error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leaves."""
        try:
            if not self.bot.db_manager:
                return

            guild_id = member.guild.id
            user_id = member.id

                        # ✅ RESET ALL USER DATA WHEN THEY LEAVE
            try:
                async with self.bot.db_manager.pool.acquire() as conn:
                    # Reset XP data
                    await conn.execute(
                        "DELETE FROM user_xp WHERE guild_id = $1 AND user_id = $2",
                        guild_id, user_id
                    )
                    
                    # Reset birthday data
                    await conn.execute(
                        "DELETE FROM birthdays WHERE user_id = $1",
                        user_id
                    )
                    
                    # Reset warnings data
                    await conn.execute(
                        "DELETE FROM warnings WHERE guild_id = $1 AND user_id = $2",
                        guild_id, user_id
                    )
                    
                    # Reset verification data
                    await conn.execute(
                        "DELETE FROM verified_users WHERE guild_id = $1 AND user_id = $2",
                        guild_id, user_id
                    )
                
                self.logger.info(f"Reset all data for user {member.name} ({user_id}) who left {member.guild.name}")
            except Exception as e:
                self.logger.error(f"Error resetting user data: {e}")

            # Get goodbye settings
            goodbye_channel_id = await self.bot.db_manager.get_setting(
                "goodbye_channel", guild_id
            )
            goodbye_title = (
                await self.bot.db_manager.get_setting("goodbye_title", guild_id)
                or DEFAULT_GOODBYE_TITLE
            )
            goodbye_message = (
                await self.bot.db_manager.get_setting("goodbye_message", guild_id)
                or DEFAULT_GOODBYE_MESSAGE
            )
            goodbye_image = await self.bot.db_manager.get_setting(
                "goodbye_image", guild_id
            )

            if not goodbye_channel_id:
                return

            channel = self.bot.get_channel(int(goodbye_channel_id))
            if not channel:
                self.logger.warning(f"Goodbye channel {goodbye_channel_id} not found")
                return

            # Format goodbye message
            formatted_message = goodbye_message.replace(
                "{member.mention}", member.mention
            )
            formatted_message = formatted_message.replace("{member.name}", member.name)
            formatted_message = formatted_message.replace(
                "{server.name}", member.guild.name
            )
            formatted_message = formatted_message.replace(
                "{member.count}", str(len(member.guild.members))
            )

            # Create goodbye embed
            embed = create_embed(
                title=goodbye_title.replace("{member.name}", member.name),
                description=formatted_message,
                color=COLORS["error"],
            )

            embed.set_thumbnail(
                url=(
                    member.display_avatar.url
                    if member.display_avatar
                    else member.default_avatar.url
                )
            )
            embed.set_footer(text=f"Member count: {len(member.guild.members)}")

            # Add image if configured
            if goodbye_image:
                embed.set_image(url=goodbye_image)

            await safe_send_message(channel, embed=embed)

            self.logger.info(
                f"Sent goodbye message for {member.name} in {member.guild.name}"
            )

        except Exception as e:
            self.logger.error(f"Error in on_member_remove: {e}")

    # DEPRECATED: Welcome command moved to /setup
    # Keeping the helper methods below for potential future use
    # @app_commands.command(name="welcome", description="Welcome system configuration (Server Owner only)")
    # @app_commands.describe(
    #     action="What welcome action would you like to perform?"
    # )
    # @app_commands.choices(action=[
    #     app_commands.Choice(name="setchannel", value="setchannel"),
    #     app_commands.Choice(name="settitle", value="settitle"),
    #     app_commands.Choice(name="setmessage", value="setmessage"),
    #     app_commands.Choice(name="setimage", value="setimage")
    # ])
    async def _welcome_deprecated(self, interaction: discord.Interaction, action: str):
        """Welcome system configuration commands."""
        try:
            # Check permissions - Both admin and owner should be able to use this
            if not (
                is_admin(interaction.user) or interaction.user.id in settings.OWNER_IDS
            ):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command is only available to bot owners.",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if not self.bot.db_manager:
                embed = embed_helper.error_embed(
                    title="Database Error", description="Database is not available."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Route to appropriate handler
            if action == "setchannel":
                await self._set_welcome_channel(interaction)
            elif action == "settitle":
                await self._set_welcome_title(interaction)
            elif action == "setmessage":
                await self._set_welcome_message(interaction)
            elif action == "setimage":
                await self._set_welcome_image(interaction)
            else:
                embed = embed_helper.error_embed(
                    title="Unknown Action",
                    description="The specified action is not recognized.",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error in welcome command: {e}")
            await self._error_response(interaction, "Failed to execute welcome command")

    async def _set_welcome_channel(self, interaction: discord.Interaction):
        """Set the welcome channel."""
        try:
            # Get all text channels
            channels = list(interaction.guild.text_channels)

            if not channels:
                embed = embed_helper.error_embed(
                    title="No Channels Found",
                    description="No text channels found in this server.",
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Create channel selection view
            class ChannelSelectView(discord.ui.View):
                def __init__(self, cog_instance):
                    super().__init__(timeout=60)
                    self.cog = cog_instance
                    self.selected_channel = None

                @discord.ui.select(
                    placeholder="Select a welcome channel",
                    options=[
                        discord.SelectOption(
                            label=channel.name,
                            value=str(channel.id),
                            description=f"#{channel.name}",
                        )
                        for channel in channels[:25]  # Discord limit is 25 options
                    ],
                )
                async def select_callback(
                    self, interaction: discord.Interaction, select: discord.ui.Select
                ):
                    self.selected_channel = int(select.values[0])
                    self.stop()

                    # Save to database
                    await self.cog.bot.db_manager.set_setting(
                        "welcome_channel_id", str(self.selected_channel)
                    )

                    channel = self.cog.bot.get_channel(self.selected_channel)
                    embed = embed_helper.success_embed(
                        title="✅ Welcome Channel Set",
                        description=f"Welcome channel has been set to {channel.mention}",
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            view = ChannelSelectView(self)
            embed = embed_helper.info_embed(
                title="📢 Select Welcome Channel",
                description="Please select the channel where welcome messages should be sent.",
            )
            await interaction.response.send_message(
                embed=embed, view=view, ephemeral=True
            )

        except Exception as e:
            self.logger.error(f"Error setting welcome channel: {e}")
            await self._error_response(interaction, "Failed to set welcome channel")

    async def _set_welcome_title(self, interaction: discord.Interaction):
        """Set the welcome message title."""
        try:
            await interaction.response.send_message(
                "Please enter the welcome message title.\n"
                "You can use {member.name} for the member's name.",
                ephemeral=True,
            )

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60.0)

                # Save to database
                await self.bot.db_manager.set_setting("welcome_title", msg.content)

                embed = embed_helper.success_embed(
                    title="✅ Welcome Title Set",
                    description=f"Welcome title has been set to:\n\n{msg.content}",
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

            except asyncio.TimeoutError:
                embed = embed_helper.error_embed(
                    title="Timeout", description="You took too long to respond."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error setting welcome title: {e}")
            await self._error_response(interaction, "Failed to set welcome title")

    async def _set_welcome_message(self, interaction: discord.Interaction):
        """Set the welcome message content."""
        try:
            await interaction.response.send_message(
                "Please enter the welcome message.\n"
                "You can use {member.mention}, {member.name}, {server.name}",
                ephemeral=True,
            )

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60.0)

                # Save to database
                await self.bot.db_manager.set_setting("welcome_message", msg.content)

                embed = embed_helper.success_embed(
                    title="✅ Welcome Message Set",
                    description=f"Welcome message has been set to:\n\n{msg.content}",
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

            except asyncio.TimeoutError:
                embed = embed_helper.error_embed(
                    title="Timeout", description="You took too long to respond."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error setting welcome message: {e}")
            await self._error_response(interaction, "Failed to set welcome message")

    async def _set_welcome_image(self, interaction: discord.Interaction):
        """Set the welcome message image URL."""
        try:
            await interaction.response.send_message(
                "Please enter the welcome image URL (or 'none' to remove image):",
                ephemeral=True,
            )

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=60.0)

                if msg.content.lower() == "none":
                    await self.bot.db_manager.set_setting("welcome_image", "")
                    image_desc = "No image"
                else:
                    await self.bot.db_manager.set_setting("welcome_image", msg.content)
                    image_desc = msg.content

                embed = embed_helper.success_embed(
                    title="✅ Welcome Image Set",
                    description=f"Welcome image has been set to: {image_desc}",
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

            except asyncio.TimeoutError:
                embed = embed_helper.error_embed(
                    title="Timeout", description="You took too long to respond."
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error setting welcome image: {e}")
            await self._error_response(interaction, "Failed to set welcome image")

    async def _error_response(self, interaction: discord.Interaction, message: str):
        """Send error response."""
        embed = embed_helper.error_embed(
            title="Welcome Command Error", description=message
        )

        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass


async def setup(bot: commands.Bot):
    """Setup function for the cog."""
    welcome_cog = Welcome(bot)
    await bot.add_cog(welcome_cog)
    # Commands are automatically registered when cog is loaded
