"""
Bot Control Cog for MalaBoT
Owner-only commands to control bot features
"""

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput

from src.config.constants import COLORS
from src.utils.helpers import create_embed
from src.utils.logger import log_system


class SendMessageModal(Modal, title="Send Message as Bot"):
    """Modal for sending a message as the bot"""

    message_content = TextInput(
        label="Message Content",
        placeholder="Enter the message you want to send...",
        required=True,
        max_length=2000,
        style=discord.TextStyle.paragraph,
    )

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Send the message to the selected channel
            await self.channel.send(self.message_content.value)

            # Confirm to the user
            embed = create_embed(
                " Message Sent",
                f"Message sent to {self.channel.mention}\n\n**Content:**\n{self.message_content.value[:100]}{'...' if len(self.message_content.value) > 100 else ''}",
                COLORS["success"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

            log_system(
                f"[BOT CONTROL] {interaction.user.name} sent message to {self.channel.name}"
            )

        except discord.Forbidden:
            embed = create_embed(
                " Permission Error",
                f"I don't have permission to send messages in {self.channel.mention}",
                COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = create_embed(
                " Error", f"Failed to send message: {str(e)}", COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


class BotControlGroup(app_commands.Group):
    """Bot control commands group"""

    def __init__(self, cog):
        super().__init__(
            name="bot", description="Bot control commands (Server Owner only)"
        )
        self.cog = cog

    async def channel_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for channel selection - shows all text channels"""
        try:
            channels = [
                app_commands.Choice(name=f"#{channel.name}", value=str(channel.id))
                for channel in interaction.guild.text_channels
                if current.lower() in channel.name.lower()
            ]
            return channels[:25]  # Discord limits to 25 choices
        except Exception:
            # If autocomplete fails (e.g., interaction already acknowledged), return empty list
            return []

    @app_commands.command(
        name="send",
        description="Send a message as the bot to a channel (Server Owner only)",
    )
    @app_commands.describe(channel="The channel to send the message to")
    @app_commands.autocomplete(channel=channel_autocomplete)
    async def send(self, interaction: discord.Interaction, channel: str):
        """Send a message as the bot to a specific channel"""

        # Check server owner permissions
        if interaction.guild.owner_id != interaction.user.id:
            embed = create_embed(
                " Permission Denied",
                "This command is only available to the server owner.",
                COLORS["error"],
            )
            # Check if already responded (from autocomplete)
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get the channel object from the ID
        try:
            channel_obj = interaction.guild.get_channel(int(channel))
        except ValueError:
            embed = create_embed(
                " Error", "Invalid channel ID.", COLORS["error"]
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        if not channel_obj or not isinstance(channel_obj, discord.TextChannel):
            embed = create_embed(
                " Error", "Invalid channel selected.", COLORS["error"]
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Open modal for message input (only if not already responded)
        modal = SendMessageModal(channel_obj)
        if not interaction.response.is_done():
            await interaction.response.send_modal(modal)


class BotControl(commands.Cog):
    """Bot control and management commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Add the command group to the bot's tree
        self.bot_group = BotControlGroup(self)
        self.bot.tree.add_command(self.bot_group)

    async def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.bot.tree.remove_command(self.bot_group.name)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotControl(bot))

