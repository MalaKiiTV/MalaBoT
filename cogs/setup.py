"""
Setup Cog for MalaBoT
Unified configuration system for all bot features
Command: /setup
"""

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput, Button, ChannelSelect
from typing import Optional

from utils.helpers import create_embed, safe_send_message
from utils.logger import log_system
from config.constants import COLORS
from cogs.role_connection_ui import (
    AddConnectionView, ManageConnectionsView, ProtectedRolesView
)


# ============================================================
# VERIFICATION SYSTEM COMPONENTS
# ============================================================

class ChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for verification review channel"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select review channel...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        try:
            await self.db.set_setting(f"verify_channel_{self.guild_id}", channel.id)
            await self.db.log_event(
                category="VERIFY",
                action="SETUP_CHANNEL",
                user_id=interaction.user.id,
                details=f"Set review channel to #{channel.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Review Channel Set",
                    f"✅ Verification submissions will be posted to {channel.mention}",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting review channel: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set review channel. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class RoleSelect(discord.ui.RoleSelect):
    """Role selector for verified role"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select verified role...",
            min_values=1,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting(f"verify_role_{self.guild_id}", role.id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_ROLE",
                user_id=interaction.user.id,
                details=f"Set verified role to {role.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Verified Role Set",
                    f"✅ Users will receive {role.mention} when verified",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting verified role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set verified role. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class CheaterRoleSelect(discord.ui.RoleSelect):
    """Role selector for cheater role"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select cheater role...",
            min_values=1,
            max_values=1
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        role = self.values[0]
        try:
            await self.db.set_setting(f"cheater_role_{self.guild_id}", role.id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_CHEATER_ROLE",
                user_id=interaction.user.id,
                details=f"Set cheater role to {role.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Role Set",
                    f"✅ Cheaters will receive {role.mention} and have all other roles removed",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting cheater role: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set cheater role. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class CheaterJailChannelSelect(discord.ui.ChannelSelect):
    """Channel selector for cheater jail"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(
            placeholder="Select cheater jail channel (optional)...",
            min_values=0,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        if not self.values:
            # Clear the channel if none selected
            await self.db.set_setting(f"cheater_jail_channel_{self.guild_id}", None)
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Jail Channel Cleared",
                    "✅ Cheater jail channel has been cleared.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
            return
            
        channel = self.values[0]
        try:
            await self.db.set_setting(f"cheater_jail_channel_{self.guild_id}", channel.id)
            await self.db.log_event(
                category="VERIFY",
                action="CONFIG_CHEATER_JAIL",
                user_id=interaction.user.id,
                details=f"Set cheater jail channel to {channel.name}",
                guild_id=self.guild_id,
            )
            await interaction.response.send_message(
                embed=create_embed(
                    "Cheater Jail Channel Set",
                    f"✅ Cheater jail channel set to {channel.mention}\n\n"
                    f"Users marked as cheaters will be moved here and have all other roles removed.",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
        except Exception as e:
            log_system(f"Error setting cheater jail channel: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set cheater jail channel. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class VerificationSetupView(View):
    """View for verification system setup"""
    def __init__(self, db_manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild = guild
        
        # Add channel and role selects
        self.add_item(ChannelSelect(db_manager, guild.id))
        self.add_item(RoleSelect(db_manager, guild.id))
        self.add_item(CheaterRoleSelect(db_manager, guild.id))
        self.add_item(CheaterJailChannelSelect(db_manager, guild.id))

    @discord.ui.button(label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current verification configuration"""
        verify_channel_id = await self.db.get_setting(f"verify_channel_{self.guild.id}")
        verify_role_id = await self.db.get_setting(f"verify_role_{self.guild.id}")
        cheater_role_id = await self.db.get_setting(f"cheater_role_{self.guild.id}")
        cheater_jail_id = await self.db.get_setting(f"cheater_jail_channel_{self.guild.id}")

        config_text = ""
        if verify_channel_id:
            config_text += f"**Review Channel:** <#{verify_channel_id}>\n"
        else:
            config_text += "**Review Channel:** Not configured\n"

        if verify_role_id:
            config_text += f"**Verified Role:** <@&{verify_role_id}>\n"
        else:
            config_text += "**Verified Role:** Not configured\n"

        if cheater_role_id:
            config_text += f"**Cheater Role:** <@&{cheater_role_id}>\n"
        else:
            config_text += "**Cheater Role:** Not configured\n"

        if cheater_jail_id:
            config_text += f"**Cheater Jail:** <#{cheater_jail_id}>\n"
        else:
            config_text += "**Cheater Jail:** Not configured\n"

        embed = discord.Embed(
            title="Current Verification Configuration",
            description=config_text,
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================================
# GENERAL SETTINGS COMPONENTS
# ============================================================

class TimezoneSelect(discord.ui.Select):
    """Dropdown for timezone selection"""
    def __init__(self, db_manager, guild_id: int):
        self.db = db_manager
        self.guild_id = guild_id
        options = [
            discord.SelectOption(label="Eastern Time (ET)", value="America/New_York"),
            discord.SelectOption(label="Central Time (CT)", value="America/Chicago"),
            discord.SelectOption(label="Mountain Time (MT)", value="America/Denver"),
            discord.SelectOption(label="Pacific Time (PT)", value="America/Los_Angeles"),
            discord.SelectOption(label="Alaska Time (AKT)", value="America/Anchorage"),
            discord.SelectOption(label="Hawaii Time (HT)", value="Pacific/Honolulu"),
            discord.SelectOption(label="Arizona Time (AZ)", value="America/Phoenix"),
        ]
        super().__init__(placeholder="Select your timezone", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting(f"timezone_{self.guild_id}", self.values[0])
            await self.db.log_event(
                category="SETTINGS",
                action="SET_TIMEZONE",
                user_id=interaction.user.id,
                details=f"Set timezone to {self.values[0]}",
                guild_id=self.guild_id,
            )
            
            # Show brief confirmation
            await interaction.response.edit_message(
                embed=create_embed(
                    "✅ Timezone Set",
                    f"Timezone set to **{self.values[0]}**",
                    COLORS["success"],
                ),
                view=None
            )
            
            # Wait 2 seconds then return to general settings
            import asyncio
            await asyncio.sleep(2)
            
            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"]
            )
            await interaction.edit_original_response(embed=embed, view=general_view)
            
        except Exception as e:
            log_system(f"Error setting timezone: {e}", level="error")
            await interaction.response.edit_message(
                embed=create_embed(
                    "❌ Error",
                    "Failed to set timezone.",
                    COLORS["error"],
                ),
                view=None
            )


class OnlineMessageChannelSelect(discord.ui.ChannelSelect):
    """Channel selection for online message"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(placeholder="Select a channel for the online message")
        self.db = db_manager
        self.guild_id = guild_id

    async def callback(self, interaction: discord.Interaction):
        channel = self.values[0]
        modal = OnlineMessageModal(self.db, self.guild_id, channel.id)
        await interaction.response.send_modal(modal)


class OnlineMessageModal(Modal, title="Set Bot Online Message"):
    """Modal for setting bot online message"""
    message = TextInput(
        label="Online Message",
        placeholder="Message to send when bot comes online",
        required=True,
        max_length=200,
        style=discord.TextStyle.paragraph
    )

    def __init__(self, db_manager, guild_id: int, channel_id: int):
        super().__init__()
        self.db = db_manager
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.db.set_setting(f"online_message_{self.guild_id}", self.message.value)
            await self.db.set_setting(f"online_message_channel_{self.guild_id}", str(self.channel_id))
            await self.db.log_event(
                category="SETTINGS",
                action="SET_ONLINE_MESSAGE",
                user_id=interaction.user.id,
                details=f"Set online message in channel {self.channel_id}",
                guild_id=self.guild_id,
            )
            channel = interaction.guild.get_channel(self.channel_id)
            channel_name = channel.name if channel else "Unknown"
            
            # Show brief confirmation
            await interaction.response.send_message(
                embed=create_embed(
                    "✅ Online Message Set",
                    f"Message set in **#{channel_name}**",
                    COLORS["success"],
                ),
                ephemeral=True,
            )
            
            # Wait 2 seconds then show general settings again
            import asyncio
            await asyncio.sleep(2)
            
            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"]
            )
            await interaction.edit_original_response(embed=embed, view=general_view)
        except Exception as e:
            log_system(f"Error setting online message: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Failed to set online message. Please try again.",
                    COLORS["error"],
                ),
                ephemeral=True,
            )


class JoinRoleSelectView(View):
    """View for selecting join role from dropdown"""
    def __init__(self, db_manager, guild_id: int, guild: discord.Guild):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id
        self.guild = guild
        
        # Get all roles except @everyone and sort by position (highest first)
        roles = [r for r in guild.roles if r.name != "@everyone"]
        roles.sort(key=lambda r: r.position, reverse=True)
        
        # Discord has a limit of 25 options per select menu
        # We'll take the top 25 roles by position
        roles = roles[:25]
        
        # Create select menu options
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id),
                description=f"Position: {role.position}",
                emoji="🎭"
            )
            for role in roles
        ]
        
        # Add the select menu
        select = discord.ui.Select(
            placeholder="Choose a role to auto-assign...",
            options=options,
            custom_id="join_role_select"
        )
        select.callback = self.role_selected
        self.add_item(select)
        
        # Add cancel button
        cancel_button = Button(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
            emoji="❌"
        )
        cancel_button.callback = self.cancel
        self.add_item(cancel_button)
    
    async def role_selected(self, interaction: discord.Interaction):
        """Handle role selection"""
        role_id = interaction.data["values"][0]
        role = self.guild.get_role(int(role_id))
        
        if not role:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not find the selected role. Please try again.",
                color=COLORS["error"]
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Wait 3 seconds then return to general settings
            import asyncio
            await asyncio.sleep(3)
            
            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"]
            )
            await interaction.edit_original_response(embed=embed, view=general_view)
            return
        
        # Save the role
        await self.db.set_setting(f"join_role_{self.guild_id}", str(role.id))
        
        # Show confirmation
        embed = discord.Embed(
            title="✅ Join Role Set",
            description=f"New members will automatically receive {role.mention}",
            color=COLORS["success"],
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Wait 2 seconds then return to general settings
        import asyncio
        await asyncio.sleep(2)
        
        general_view = GeneralSettingsView(self.db, self.guild_id)
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"]
        )
        await interaction.edit_original_response(embed=embed, view=general_view)
    
    async def cancel(self, interaction: discord.Interaction):
        """Cancel and return to general settings"""
        general_view = GeneralSettingsView(self.db, self.guild_id)
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"]
        )
        await interaction.response.edit_message(embed=embed, view=general_view)


class GeneralSettingsView(View):
    """View for general settings setup"""
    def __init__(self, db_manager, guild_id: int):
        super().__init__(timeout=300)
        self.db = db_manager
        self.guild_id = guild_id

    async def show_general_settings(self, interaction: discord.Interaction, is_followup: bool = False):
        """Show the general settings menu"""
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"]
        )
        new_view = GeneralSettingsView(self.db, self.guild_id)
        
        # Always edit the original message to avoid creating duplicates
        await interaction.message.edit(embed=embed, view=new_view)

    @discord.ui.button(label="Set Timezone", style=discord.ButtonStyle.primary, emoji="🌍")
    async def set_timezone(self, interaction: discord.Interaction, button: Button):
        """Set server timezone"""
        view = discord.ui.View()
        view.add_item(TimezoneSelect(self.db, self.guild_id))
        
        embed = discord.Embed(
            title="🌍 Select Timezone",
            description="Choose your server's timezone.",
            color=COLORS["primary"]
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Set Online Message", style=discord.ButtonStyle.primary, emoji="💬")
    async def set_online_message(self, interaction: discord.Interaction, button: Button):
        """Set bot online message"""
        view = View()
        view.add_item(OnlineMessageChannelSelect(self.db, self.guild_id))
        
        embed = discord.Embed(
            title="💬 Set Online Message",
            description="Select a channel for the online message.",
            color=COLORS["primary"]
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Set Mod Role", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def set_mod_role(self, interaction: discord.Interaction, button: Button):
        """Set mod role for command permissions"""
        select = discord.ui.RoleSelect(
            placeholder="Select the mod role...",
            min_values=1,
            max_values=1
        )
        
        async def role_callback(interaction: discord.Interaction):
            role = select.values[0]
            await self.db.set_setting(f"mod_role_{self.guild_id}", str(role.id))
            
            # Show brief confirmation
            embed = discord.Embed(
                title="✅ Mod Role Set",
                description=f"Mod role set to {role.mention}",
                color=COLORS["success"],
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Wait 2 seconds then return to general settings
            import asyncio
            await asyncio.sleep(2)
            
            general_view = GeneralSettingsView(self.db, self.guild_id)
            embed = discord.Embed(
                title="⚙️ General Settings",
                description="Click the buttons below to configure each setting.",
                color=COLORS["primary"]
            )
            await interaction.edit_original_response(embed=embed, view=general_view)
        
        select.callback = role_callback
        view = View(timeout=60)
        view.add_item(select)
        
        embed = discord.Embed(
            title="🛡️ Select Mod Role",
            description="Choose the mod role.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Set Join Role", style=discord.ButtonStyle.primary, emoji="👋")
    async def set_join_role(self, interaction: discord.Interaction, button: Button):
        """Set role to auto-assign to new members"""
        # Create a view with role selection dropdown
        view = JoinRoleSelectView(self.db, self.guild_id, interaction.guild)
        
        embed = discord.Embed(
            title="👋 Set Join Role",
            description="Select a role from the dropdown below to auto-assign to new members.\n\n"
                       "**Note:** The role must be below the bot's highest role in the role hierarchy.",
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="View Current Config", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def view_config(self, interaction: discord.Interaction, button: Button):
        """View current general settings"""
        timezone = await self.db.get_setting(f"timezone_{self.guild_id}", "UTC-6")
        online_message = await self.db.get_setting(f"online_message_{self.guild_id}", "Not set")
        online_channel_id = await self.db.get_setting(f"online_message_channel_{self.guild_id}")
        mod_role_id = await self.db.get_setting(f"mod_role_{self.guild_id}")
        join_role_id = await self.db.get_setting(f"join_role_{self.guild_id}")
        
        mod_role_text = "Not set"
        if mod_role_id:
            try:
                mod_role = interaction.guild.get_role(int(mod_role_id))
                if mod_role:
                    mod_role_text = f"{mod_role.name}"
                else:
                    mod_role_text = f"<@&{mod_role_id}>"
            except:
                mod_role_text = f"<@&{mod_role_id}>"
        
        join_role_text = "Not set"
        if join_role_id:
            try:
                join_role = interaction.guild.get_role(int(join_role_id))
                if join_role:
                    join_role_text = f"{join_role.name}"
                else:
                    join_role_text = f"<@&{join_role_id}>"
            except:
                join_role_text = f"<@&{join_role_id}>"
        
        online_channel_text = "Not set"
        if online_channel_id:
            online_channel_text = f"<#{online_channel_id}>"

        config_text = f"**Timezone:** {timezone}\n**Online Message:** {online_message}\n**Online Channel:** {online_channel_text}\n**Mod Role:** {mod_role_text}\n**Join Role:** {join_role_text}"

        embed = discord.Embed(
            title="Current General Settings",
            description=config_text,
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================================
# ROLE CONNECTION SYSTEM COMPONENTS
# ============================================================

class RoleConnectionSetupView(View):
    """Main view for role connection management"""
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.add_item(RoleConnectionMainSelect(manager, guild))

class RoleConnectionMainSelect(Select):
    """Main menu for role connections"""
    def __init__(self, manager, guild: discord.Guild):
        self.manager = manager
        self.guild = guild
        options = [
            discord.SelectOption(
                label="Add Connection",
                value="add",
                description="Create a new role connection rule",
                emoji="➕"
            ),
            discord.SelectOption(
                label="Manage Connections",
                value="manage",
                description="View, edit, or delete existing connections",
                emoji="📝"
            ),
            discord.SelectOption(
                label="Protected Roles",
                value="protected",
                description="Manage roles exempt from connections",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="Back to Setup",
                value="back",
                description="Return to main setup menu",
                emoji="◀️"
            ),
        ]
        super().__init__(
            placeholder="Select an option...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        if selection == "add":
            await self.add_connection(interaction)
        elif selection == "manage":
            await self.manage_connections(interaction)
        elif selection == "protected":
            await self.manage_protected_roles(interaction)
        elif selection == "back":
            await self.back_to_setup(interaction)

    async def add_connection(self, interaction: discord.Interaction):
        """Start the process of adding a new connection"""
        view = AddConnectionView(self.manager, self.guild)
        
        embed = discord.Embed(
            title="➕ Add Role Connection",
            description=(
                "**Step 1: Select Target Role**\n"
                "Choose the role that will be given or removed.\n\n"
                "After selecting the role, you'll configure:\n"
                "• Action (Give or Remove)\n"
                "• Conditions (Has/Doesn't Have roles)\n"
                "• Logic (AND/OR)"
            ),
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

    async def manage_connections(self, interaction: discord.Interaction):
        """Show list of connections to manage"""
        # Force reload from database to ensure fresh data
        self.manager.connections_cache[self.guild.id] = []  # Clear cache
        await self.manager.load_connections(self.guild.id)
        connections = self.manager.connections_cache.get(self.guild.id, [])
        
        if not connections:
            await interaction.response.send_message(
                embed=create_embed(
                    "No Connections",
                    "No role connections have been configured yet.\nUse 'Add Connection' to create one.",
                    COLORS["warning"]
                ),
                ephemeral=True
            )
            return
        
        view = ManageConnectionsView(self.manager, self.guild, connections)
        
        embed = discord.Embed(
            title="📝 Manage Connections",
            description="Select a connection to toggle, edit, or delete:",
            color=COLORS["primary"]
        )
        
        for i, conn in enumerate(connections[:25], 1):
            target_role = self.guild.get_role(conn.target_role_id)
            if target_role:
                status = "✅ Enabled" if conn.enabled else "❌ Disabled"
                
                # Build condition text
                cond_text = []
                for cond in conn.conditions:
                    role = self.guild.get_role(cond["role_id"])
                    if role:
                        cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                        cond_text.append(f"{cond_type} {role.name}")
                
                conditions_str = f" {conn.logic} ".join(cond_text) if cond_text else "No conditions"
                
                embed.add_field(
                    name=f"{i}. {conn.action.title()} {target_role.name} ({status})",
                    value=f"When: {conditions_str}",
                    inline=False
                )
        
        await interaction.response.edit_message(embed=embed, view=view)

    async def manage_protected_roles(self, interaction: discord.Interaction):
        """Manage protected roles"""
        await self.manager.load_protected_roles(self.guild.id)
        protected = self.manager.protected_roles_cache.get(self.guild.id, [])
        
        view = ProtectedRolesView(self.manager, self.guild)
        
        embed = discord.Embed(
            title="🛡️ Protected Roles",
            description=(
                "Users with protected roles are exempt from ALL role connection rules.\n\n"
                "**Current Protected Roles:**"
            ),
            color=COLORS["primary"]
        )
        
        if protected:
            role_list = []
            for role_id in protected:
                role = self.guild.get_role(role_id)
                if role:
                    role_list.append(f"• {role.mention}")
            embed.add_field(name="Protected", value="\n".join(role_list) or "None", inline=False)
        else:
            embed.add_field(name="Protected", value="*No protected roles set*", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)

    async def back_to_setup(self, interaction: discord.Interaction):
        """Return to main setup menu"""
        view = SetupView()
        
        embed = discord.Embed(
            title="⚙️ MalaBoT Setup",
            description="Select a system to configure:",
            color=COLORS["primary"]
        )
        
        await interaction.response.edit_message(embed=embed, view=view)


# ============================================================
# MAIN SETUP SELECT MENU
# ============================================================

class SetupSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Verification System",
                value="verification",
                description="Configure verification channels and roles",
                emoji="✅"
            ),
            discord.SelectOption(
                label="Welcome System",
                value="welcome",
                description="Configure welcome messages and channel",
                emoji="👋"
            ),
            discord.SelectOption(
                label="Birthday System",
                value="birthday",
                description="Configure birthday announcements",
                emoji="🎂"
            ),
            discord.SelectOption(
                label="XP System",
                value="xp",
                description="Configure XP and leveling settings",
                emoji="🏆"
            ),
            discord.SelectOption(
                label="General Settings",
                value="general",
                description="Configure timezone, online message, etc.",
                emoji="⚙️"
            ),
            discord.SelectOption(
                label="Role Connections",
                value="role_connections",
                description="Configure automatic role assignment rules",
                emoji="🔗"
            ),
            discord.SelectOption(
                label="View Current Config",
                value="view",
                description="View all current bot settings",
                emoji="📋"
            ),
        ]
        super().__init__(
            placeholder="Select a system to configure...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        if selection == "verification":
            await self.setup_verification(interaction)
        elif selection == "welcome":
            await self.setup_welcome(interaction)
        elif selection == "birthday":
            await self.setup_birthday(interaction)
        elif selection == "xp":
            await self.setup_xp(interaction)
        elif selection == "general":
            await self.setup_general(interaction)
        elif selection == "role_connections":
            await self.setup_role_connections(interaction)
        elif selection == "view":
            await self.view_config(interaction)

    async def setup_verification(self, interaction: discord.Interaction):
        """Setup verification system with interactive configuration"""
        view = VerificationSetupView(interaction.client.db_manager, interaction.guild)
        
        embed = discord.Embed(
            title="✅ Verification System Setup",
            description=(
                "Configure your verification system using the dropdowns below:\n\n"
                "**Required Settings:**\n"
                "• Review Channel - Where staff sees verification submissions\n"
                "• Verified Role - Role assigned when user is verified\n\n"
                "**User Workflow:**\n"
                "1. User runs `/verify submit`\n"
                "2. Enters Activision ID in modal\n"
                "3. Uploads screenshot\n"
                "4. Selects platform from dropdown\n"
                "5. Staff reviews with `/verify review @user verified/cheater/unverified`\n\n"
                "**Review Decisions:**\n"
                "• Verified - Assigns verified role\n"
                "• Cheater - Bans user from server\n"
                "• Unverified - Leaves user unverified"
            ),
            color=COLORS["info"],
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def setup_welcome(self, interaction: discord.Interaction):
        """Setup welcome system"""
        embed = discord.Embed(
            title="👋 Welcome System Setup",
            description=(
                "Configure your welcome system:\n\n"
                "**Available Variables:**\n"
                "`{member}` - Mentions the new member\n"
                "`{member.name}` - Member's username\n"
                "`{server}` - Server name\n"
                "`{member.count}` - Total member count\n\n"
                "Click the buttons below to configure each setting."
            ),
            color=COLORS["welcome"],
        )
        
        view = WelcomeSetupView(interaction.guild.id, interaction.client.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)

    async def setup_birthday(self, interaction: discord.Interaction):
        """Setup birthday system"""
        embed = discord.Embed(
            title="🎂 Birthday System Setup",
            description=(
                "Configure your birthday system:\n\n"
                "**Available Variables:**\n"
                "`{member}` - Mentions the birthday person\n"
                "`{member.name}` - Member's username\n"
                "`{age}` - Age (if year provided)\n\n"
                "**User Commands:**\n"
                "`/bday set <MM-DD>` - Users set their birthday\n"
                "`/bday view [@user]` - View birthday\n"
                "`/bday list` - View all birthdays\n"
                "`/bday next` - See next upcoming birthday\n\n"
                "Click the buttons below to configure each setting."
            ),
            color=COLORS["birthday"],
        )
        
        view = BirthdaySetupView(interaction.guild.id, interaction.client.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)

    async def setup_xp(self, interaction: discord.Interaction):
        """Setup XP system"""
        embed = discord.Embed(
            title="🏆 XP System Setup",
            description=(
                "Configure your XP system:\n\n"
                "**User Commands:**\n"
                "`/xp rank [@user]` - View XP rank\n"
                "`/xp leaderboard` - View server leaderboard\n"
                "`/xp daily` - Claim daily XP bonus\n\n"
                "**Default Settings:**\n"
                "• Users gain 5-15 XP per message\n"
                "• 60 second cooldown between XP gains\n"
                "• Daily check-in: 50 XP + streak bonus\n\n"
                "Click the buttons below to configure XP settings."
            ),
            color=COLORS["xp"],
        )
        
        view = XPSetupView(interaction.guild.id, interaction.client.db_manager)
        await interaction.response.edit_message(embed=embed, view=view)

    async def setup_general(self, interaction: discord.Interaction):
        """Setup general settings with interactive configuration"""
        view = GeneralSettingsView(interaction.client.db_manager, interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ General Settings",
            description="Click the buttons below to configure each setting.",
            color=COLORS["primary"],
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def view_config(self, interaction: discord.Interaction):
        """View current configuration"""
        bot = interaction.client
        db = bot.db_manager
        guild_id = interaction.guild.id

        # Fetch all settings
        verify_channel_id = await db.get_setting(f"verify_channel_{guild_id}")
        verify_role_id = await db.get_setting(f"verify_role_{guild_id}")
        cheater_role_id = await db.get_setting(f"cheater_role_{guild_id}")
        cheater_jail_id = await db.get_setting(f"cheater_jail_channel_{guild_id}")
        mod_role_id = await db.get_setting(f"mod_role_{guild_id}")
        welcome_channel_id = await db.get_setting("welcome_channel_id")
        welcome_message = await db.get_setting("welcome_message")
        birthday_channel_id = await db.get_setting(f"birthday_channel_{guild_id}")
        birthday_time = await db.get_setting(f"birthday_time_{guild_id}")
        birthday_message = await db.get_setting(f"birthday_message_{guild_id}")
        xp_channel_id = await db.get_setting(f"xp_channel_{guild_id}")
        xp_min = await db.get_setting(f"xp_min_{guild_id}", "5")
        xp_max = await db.get_setting(f"xp_max_{guild_id}", "15")
        timezone = await db.get_setting(f"timezone_{guild_id}", "UTC-6")
        online_message = await db.get_setting(f"online_message_{guild_id}", "Not set")

        embed = discord.Embed(
            title="📋 Current Bot Configuration",
            description=f"Configuration for **{interaction.guild.name}**",
            color=COLORS["info"],
        )

        # Verification settings
        verify_text = ""
        if verify_channel_id:
            verify_text += f"Review Channel: <#{verify_channel_id}>\n"
        if verify_role_id:
            verify_text += f"Verified Role: <@&{verify_role_id}>\n"
        if cheater_role_id:
            verify_text += f"Cheater Role: <@&{cheater_role_id}>\n"
        if cheater_jail_id:
            verify_text += f"Cheater Jail: <#{cheater_jail_id}>\n"
        if not verify_text:
            verify_text = "Not configured"
        embed.add_field(name="✅ Verification", value=verify_text, inline=False)

        # Welcome settings
        welcome_text = ""
        if welcome_channel_id:
            welcome_text += f"Channel: <#{welcome_channel_id}>\n"
            if welcome_message:
                welcome_text += f"Message: {welcome_message[:50]}{'...' if len(welcome_message) > 50 else ''}\n"
        else:
            welcome_text = "Not configured"
        embed.add_field(name="👋 Welcome", value=welcome_text, inline=False)

        # Birthday settings
        birthday_text = ""
        if birthday_channel_id:
            birthday_text += f"Channel: <#{birthday_channel_id}>\n"
            if birthday_time:
                birthday_text += f"Time: {birthday_time}\n"
            if birthday_message:
                birthday_text += f"Message: {birthday_message[:50]}{'...' if len(birthday_message) > 50 else ''}\n"
        else:
            birthday_text = "Not configured"
        embed.add_field(name="🎂 Birthday", value=birthday_text, inline=False)
        
        # XP settings
        xp_text = ""
        if xp_channel_id:
            xp_text += f"Level-up Channel: <#{xp_channel_id}>\n"
        xp_text += f"XP per Message: {xp_min}-{xp_max}\n"
        embed.add_field(name="🏆 XP System", value=xp_text, inline=False)

        # General settings
        online_channel_id = await db.get_setting(f"online_message_channel_{guild_id}")
        join_role_id = await db.get_setting(f"join_role_{guild_id}")
        general_text = f"Timezone: {timezone}\nOnline Message: {online_message}"
        if online_channel_id:
            general_text += f"\nOnline Channel: <#{online_channel_id}>"
        if mod_role_id:
            general_text += f"\nMod Role: <@&{mod_role_id}>"
        if join_role_id:
            general_text += f"\nJoin Role: <@&{join_role_id}>"
        embed.add_field(name="⚙️ General", value=general_text, inline=False)

        # Role Connections settings
        role_conn_cog = interaction.client.get_cog("RoleConnections")
        if role_conn_cog:
            manager = role_conn_cog.manager
            await manager.load_connections(guild_id)
            await manager.load_protected_roles(guild_id)
            
            connections = manager.connections_cache.get(guild_id, [])
            protected_roles = manager.protected_roles_cache.get(guild_id, [])
            
            active_count = sum(1 for conn in connections if conn.enabled)
            disabled_count = sum(1 for conn in connections if not conn.enabled)
            
            role_conn_text = f"Active Connections: {active_count}\n"
            role_conn_text += f"Disabled Connections: {disabled_count}\n"
            role_conn_text += f"Protected Roles: {len(protected_roles)}"
            
            embed.add_field(name="🔗 Role Connections", value=role_conn_text, inline=False)

        await interaction.response.edit_message(embed=embed, view=None)

    async def setup_role_connections(self, interaction: discord.Interaction):
        """Setup role connections system"""
        # Get the role connections manager from the bot
        role_conn_cog = interaction.client.get_cog("RoleConnections")
        if not role_conn_cog:
            await interaction.response.send_message(
                embed=create_embed(
                    "Error",
                    "Role Connections system is not loaded. Please contact an administrator.",
                    COLORS["error"]
                ),
                ephemeral=True
            )
            return
        
        manager = role_conn_cog.manager
        await manager.load_connections(interaction.guild.id)
        await manager.load_protected_roles(interaction.guild.id)
        
        view = RoleConnectionSetupView(manager, interaction.guild)
        
        embed = discord.Embed(
            title="🔗 Role Connection System",
            description=(
                "Automatically assign or remove roles based on conditions.\n\n"
                "**How it works:**\n"
                "• Create rules that give/remove roles when conditions are met\n"
                "• Conditions: User HAS or DOESN'T HAVE specific roles\n"
                "• Logic: Combine conditions with AND/OR\n"
                "• Protected Roles: Users with these roles are exempt from all rules\n\n"
                "**Example Rules:**\n"
                "• Give 'Sus' when user doesn't have 'Mala'\n"
                "• Give 'VIP' when user has 'Subscriber' AND 'Active'\n"
                "• Remove 'Guest' when user has 'Member'"
            ),
            color=COLORS["primary"]
        )
        
        # Show current connections
        connections = manager.connections_cache.get(interaction.guild.id, [])
        if connections:
            conn_text = ""
            for i, conn in enumerate(connections[:10], 1):
                target_role = interaction.guild.get_role(conn.target_role_id)
                if target_role:
                    status = "✅" if conn.enabled else "❌"
                    conn_text += f"{status} {i}. {conn.action.title()} **{target_role.name}**\n"
            embed.add_field(name="Active Connections", value=conn_text or "None", inline=False)
        
        # Show protected roles
        protected = manager.protected_roles_cache.get(interaction.guild.id, [])
        if protected:
            protected_text = " ".join([f"<@&amp;{role_id}>" for role_id in protected[:10]])
            embed.add_field(name="🛡️ Protected Roles", value=protected_text, inline=False)
        
        await interaction.response.edit_message(embed=embed, view=view)


class SetupView(View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(SetupSelect())


class WelcomeSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager
        
    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set welcome channel"""
        view = View()
        select = ChannelSelect(
            placeholder="Select welcome channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        
        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting("welcome_channel_id", str(channel.id))
            embed = discord.Embed(
                title="✅ Welcome Channel Set",
                description=f"Welcome messages will be sent to {channel.mention}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = channel_callback
        view.add_item(select)
        
        embed = discord.Embed(
            title="📢 Select Welcome Channel",
            description="Choose the channel where welcome messages will be sent.",
            color=COLORS["primary"]
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set welcome message"""
        modal = Modal(title="Set Welcome Message")
        message_input = discord.ui.TextInput(
            label="Welcome Message",
            default="Welcome {member} to {server}!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        modal.add_item(message_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting("welcome_message", message_input.value)
            embed = discord.Embed(
                title="✅ Welcome Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Title", style=ButtonStyle.primary, emoji="📝")
    async def set_title(self, interaction: discord.Interaction, button: Button):
        """Set welcome title"""
        modal = Modal(title="Set Welcome Title")
        title_input = discord.ui.TextInput(
            label="Welcome Title",
            placeholder="Welcome to the Server!",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        modal.add_item(title_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting("welcome_title", title_input.value)
            embed = discord.Embed(
                title="✅ Welcome Title Set",
                description=f"Title: {title_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Image", style=ButtonStyle.primary, emoji="🖼️")
    async def set_image(self, interaction: discord.Interaction, button: Button):
        """Set welcome image"""
        modal = Modal(title="Set Welcome Image")
        image_input = discord.ui.TextInput(
            label="Image URL",
            placeholder="https://example.com/image.png",
            style=discord.TextStyle.short,
            required=False,
            max_length=500
        )
        modal.add_item(image_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting("welcome_image", image_input.value or "")
            embed = discord.Embed(
                title="✅ Welcome Image Set",
                description=f"Image URL: {image_input.value or 'None (removed)'}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)




class GoodbyeSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager
        
    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set goodbye channel"""
        view = View()
        select = ChannelSelect(
            placeholder="Select goodbye channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        
        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(f"goodbye_channel_{self.guild_id}", str(channel.id))
            embed = discord.Embed(
                title="✅ Goodbye Channel Set",
                description=f"Goodbye messages will be sent to {channel.mention}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = channel_callback
        view.add_item(select)
        
        embed = discord.Embed(
            title="📢 Select Goodbye Channel",
            description="Choose the channel where goodbye messages will be sent.",
            color=COLORS["primary"]
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set goodbye message"""
        modal = Modal(title="Set Goodbye Message")
        message_input = discord.ui.TextInput(
            label="Goodbye Message",
            default="{member.name} has left {server}. We'll miss you!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        modal.add_item(message_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"goodbye_message_{self.guild_id}", message_input.value)
            embed = discord.Embed(
                title="✅ Goodbye Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Title", style=ButtonStyle.primary, emoji="📝")
    async def set_title(self, interaction: discord.Interaction, button: Button):
        """Set goodbye title"""
        modal = Modal(title="Set Goodbye Title")
        title_input = discord.ui.TextInput(
            label="Goodbye Title",
            placeholder="Goodbye!",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        modal.add_item(title_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"goodbye_title_{self.guild_id}", title_input.value)
            embed = discord.Embed(
                title="✅ Goodbye Title Set",
                description=f"Title: {title_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Image", style=ButtonStyle.primary, emoji="🖼️")
    async def set_image(self, interaction: discord.Interaction, button: Button):
        """Set goodbye image"""
        modal = Modal(title="Set Goodbye Image")
        image_input = discord.ui.TextInput(
            label="Image URL",
            placeholder="https://example.com/image.png",
            style=discord.TextStyle.short,
            required=False,
            max_length=500
        )
        modal.add_item(image_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"goodbye_image_{self.guild_id}", image_input.value or "")
            embed = discord.Embed(
                title="✅ Goodbye Image Set",
                description=f"Image URL: {image_input.value or 'None (removed)'}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)




class GoodbyeSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager
        
    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set goodbye channel"""
        view = View()
        select = ChannelSelect(
            placeholder="Select goodbye channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        
        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(f"goodbye_channel_{self.guild_id}", str(channel.id))
            embed = discord.Embed(
                title="✅ Goodbye Channel Set",
                description=f"Goodbye messages will be sent to {channel.mention}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = channel_callback
        view.add_item(select)
        
        embed = discord.Embed(
            title="📢 Select Goodbye Channel",
            description="Choose the channel where goodbye messages will be sent.",
            color=COLORS["primary"]
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set goodbye message"""
        modal = Modal(title="Set Goodbye Message")
        message_input = discord.ui.TextInput(
            label="Goodbye Message",
            default="{member.name} has left {server}. We'll miss you!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        modal.add_item(message_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"goodbye_message_{self.guild_id}", message_input.value)
            embed = discord.Embed(
                title="✅ Goodbye Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Title", style=ButtonStyle.primary, emoji="📝")
    async def set_title(self, interaction: discord.Interaction, button: Button):
        """Set goodbye title"""
        modal = Modal(title="Set Goodbye Title")
        title_input = discord.ui.TextInput(
            label="Goodbye Title",
            placeholder="Goodbye!",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        modal.add_item(title_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"goodbye_title_{self.guild_id}", title_input.value)
            embed = discord.Embed(
                title="✅ Goodbye Title Set",
                description=f"Title: {title_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Image", style=ButtonStyle.primary, emoji="🖼️")
    async def set_image(self, interaction: discord.Interaction, button: Button):
        """Set goodbye image"""
        modal = Modal(title="Set Goodbye Image")
        image_input = discord.ui.TextInput(
            label="Image URL",
            placeholder="https://example.com/image.png",
            style=discord.TextStyle.short,
            required=False,
            max_length=500
        )
        modal.add_item(image_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"goodbye_image_{self.guild_id}", image_input.value or "")
            embed = discord.Embed(
                title="✅ Goodbye Image Set",
                description=f"Image URL: {image_input.value or 'None (removed)'}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)


class BirthdaySetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager
        
    @discord.ui.button(label="Set Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set birthday announcement channel"""
        view = View()
        select = ChannelSelect(
            placeholder="Select birthday announcement channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        
        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(f"birthday_channel_{self.guild_id}", str(channel.id))
            embed = discord.Embed(
                title="✅ Birthday Channel Set",
                description=f"Birthday announcements will be sent to {channel.mention}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = channel_callback
        view.add_item(select)
        
        embed = discord.Embed(
            title="📢 Select Birthday Channel",
            description="Choose the channel where birthday announcements will be sent.",
            color=COLORS["primary"]
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Set Time", style=ButtonStyle.primary, emoji="⏰")
    async def set_time(self, interaction: discord.Interaction, button: Button):
        """Set birthday announcement time"""
        modal = Modal(title="Set Birthday Announcement Time")
        time_input = discord.ui.TextInput(
            label="Announcement Time (24-hour format)",
            placeholder="08:00",
            style=discord.TextStyle.short,
            required=True,
            max_length=5
        )
        modal.add_item(time_input)
        
        async def modal_callback(interaction: discord.Interaction):
            # Validate time format
            try:
                hour, minute = time_input.value.split(":")
                hour = int(hour)
                minute = int(minute)
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
                
                await self.db_manager.set_setting(f"birthday_time_{self.guild_id}", time_input.value)
                embed = discord.Embed(
                    title="✅ Birthday Time Set",
                    description=f"Announcements will be posted at {time_input.value} (server timezone)",
                    color=COLORS["success"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                embed = discord.Embed(
                    title="❌ Invalid Time Format",
                    description="Please use 24-hour format (HH:MM), e.g., 08:00 or 14:30",
                    color=COLORS["error"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set birthday message"""
        modal = Modal(title="Set Birthday Message")
        message_input = discord.ui.TextInput(
            label="Birthday Message",
            default="🎂 Happy Birthday {member}! Have a great day!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        modal.add_item(message_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"birthday_message_{self.guild_id}", message_input.value)
            embed = discord.Embed(
                title="✅ Birthday Message Set",
                description=f"Message: {message_input.value}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)


class XPSetupView(View):
    def __init__(self, guild_id: int, db_manager):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db_manager = db_manager
        
    @discord.ui.button(label="Set Level-up Channel", style=ButtonStyle.primary, emoji="📢")
    async def set_channel(self, interaction: discord.Interaction, button: Button):
        """Set level-up announcement channel"""
        view = View()
        select = ChannelSelect(
            placeholder="Select level-up announcement channel",
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1
        )
        
        async def channel_callback(interaction: discord.Interaction):
            channel = select.values[0]
            await self.db_manager.set_setting(f"xp_channel_{self.guild_id}", str(channel.id))
            embed = discord.Embed(
                title="✅ Level-up Channel Set",
                description=f"Level-up announcements will be sent to {channel.mention}",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        select.callback = channel_callback
        view.add_item(select)
        
        embed = discord.Embed(
            title="📢 Select Level-up Channel",
            description="Choose the channel where level-up announcements will be sent.",
            color=COLORS["primary"]
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Set XP Rates", style=ButtonStyle.primary, emoji="⚡")
    async def set_rates(self, interaction: discord.Interaction, button: Button):
        """Set XP gain rates"""
        modal = Modal(title="Set XP Gain Rates")
        min_xp = discord.ui.TextInput(
            label="Minimum XP per message",
            placeholder="5",
            style=discord.TextStyle.short,
            required=True,
            max_length=3
        )
        max_xp = discord.ui.TextInput(
            label="Maximum XP per message",
            placeholder="15",
            style=discord.TextStyle.short,
            required=True,
            max_length=3
        )
        modal.add_item(min_xp)
        modal.add_item(max_xp)
        
        async def modal_callback(interaction: discord.Interaction):
            try:
                min_val = int(min_xp.value)
                max_val = int(max_xp.value)
                
                if min_val < 1 or max_val < min_val:
                    raise ValueError
                
                await self.db_manager.set_setting(f"xp_min_{self.guild_id}", str(min_val))
                await self.db_manager.set_setting(f"xp_max_{self.guild_id}", str(max_val))
                
                embed = discord.Embed(
                    title="✅ XP Rates Set",
                    description=f"Users will gain {min_val}-{max_val} XP per message",
                    color=COLORS["success"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                embed = discord.Embed(
                    title="❌ Invalid Values",
                    description="Please enter valid numbers. Min must be at least 1, and Max must be greater than Min.",
                    color=COLORS["error"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Set Level-up Message", style=ButtonStyle.primary, emoji="💬")
    async def set_message(self, interaction: discord.Interaction, button: Button):
        """Set level-up message"""
        modal = Modal(title="Set Level-up Message")
        message_input = discord.ui.TextInput(
            label="Level-up Message",
            default="🎉 {member} reached level {level}!",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        modal.add_item(message_input)
        
        async def modal_callback(interaction: discord.Interaction):
            await self.db_manager.set_setting(f"xp_levelup_message_{self.guild_id}", message_input.value)
            embed = discord.Embed(
                title="✅ Level-up Message Set",
                description=f"Message: {message_input.value}\n\nAvailable variables: `{{member}}`, `{{level}}`",
                color=COLORS["success"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db_manager

    @app_commands.command(name="setup", description="Configure bot settings (Server Owner only)")
    async def setup(self, interaction: discord.Interaction):
        """Main setup command with interactive menu"""
        # Check if user is server owner
        if interaction.guild.owner_id != interaction.user.id:
            embed = discord.Embed(
                title="🚫 Permission Denied",
                description="This command is only available to the server owner.",
                color=COLORS["error"],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            title="🤖 MalaBoT Setup",
            description=(
                "Welcome to the MalaBoT configuration system!\n\n"
                "Select a system below to configure it. Each system has its own set of commands and settings.\n\n"
                "**Available Systems:**\n"
                "✅ Verification - User verification system\n"
                "👋 Welcome - Welcome messages for new members\n"
                "🎂 Birthday - Birthday announcements\n"
                "🏆 XP - Experience and leveling system\n"
                "⚙️ General - Timezone, online message, and other settings\n"
                "📋 View Config - See current configuration"
            ),
            color=COLORS["primary"],
        )
        embed.set_footer(text="Select an option from the dropdown below")

        view = SetupView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))