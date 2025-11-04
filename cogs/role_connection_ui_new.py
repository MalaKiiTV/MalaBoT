import discord
from discord import app_commands, ui
from discord.ext import commands
import json
from typing import Optional, List, Dict
from utils.logger import log_system
from utils.helpers import create_embed
from config.constants import COLORS

class RoleConnectionModal(ui.Modal, title="Create Role Connection Rule"):
    """All-in-one modal for creating role connection rules"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=600)  # 10 minute timeout for complex setup
        self.manager = manager
        self.guild = guild
        
        # Get available roles for dropdowns
        self.available_roles = [r for r in guild.roles if r.name != "@everyone"]
        self.role_options = [
            discord.SelectOption(
                label=role.name[:25],  # Discord limit is 25 chars for labels
                value=str(role.id),
                description=f"ID: {role.id}"
            ) for role in self.available_roles[:25]  # Discord limit is 25 options
        ]
        
        # Add components
        self.add_item(RoleConnectionTargetRoleSelect(self.role_options))
        self.add_item(RoleConnectionActionSelect())
        self.add_item(RoleConnectionConditionsSelect(self.role_options))
        self.add_item(RoleConnectionLogicSelect())

class RoleConnectionTargetRoleSelect(ui.Select):
    """Select the target role for the connection"""
    
    def __init__(self, role_options):
        super().__init__(
            placeholder="Select Target Role (the role to give/remove)",
            min_values=1,
            max_values=1,
            options=role_options[:25]
        )
    
    async def callback(self, interaction: discord.Interaction):
        # This will be handled by the parent modal
        pass

class RoleConnectionActionSelect(ui.Select):
    """Select the action to perform"""
    
    def __init__(self):
        super().__init__(
            placeholder="Select Action",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="Give Role",
                    value="give",
                    description="Assign role when conditions are met"
                ),
                discord.SelectOption(
                    label="Remove Role", 
                    value="remove",
                    description="Remove role when conditions are met"
                )
            ]
        )
    
    async def callback(self, interaction: discord.Interaction):
        pass

class RoleConnectionConditionsSelect(ui.Select):
    """Select multiple condition roles"""
    
    def __init__(self, role_options):
        super().__init__(
            placeholder="Select Condition Roles (roles to check for)",
            min_values=1,
            max_values=10,  # Allow up to 10 conditions
            options=role_options[:25]
        )
    
    async def callback(self, interaction: discord.Interaction):
        pass

class RoleConnectionLogicSelect(ui.Select):
    """Select the logic operator"""
    
    def __init__(self):
        super().__init__(
            placeholder="Logic: How to combine conditions?",
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label="AND (All conditions must be met)",
                    value="AND",
                    description="User must have ALL selected roles"
                ),
                discord.SelectOption(
                    label="OR (Any condition can be met)",
                    value="OR", 
                    description="User must have ANY of the selected roles"
                )
            ]
        )
    
    async def callback(self, interaction: discord.Interaction):
        pass

class RoleConnectionConditionTypeView(ui.View):
    """View for selecting condition types (HAS/DOESN'T HAVE)"""
    
    def __init__(self, selected_roles: List[discord.Role], callback_func):
        super().__init__(timeout=300)
        self.selected_roles = selected_roles
        self.callback_func = callback_func
        self.condition_types = {}  # role_id: condition_type
        
        # Create buttons for each role
        for role in selected_roles:
            self.add_item(ConditionTypeButton(role, self))

class ConditionTypeButton(ui.Button):
    """Button for setting condition type for a specific role"""
    
    def __init__(self, role: discord.Role, parent_view):
        super().__init__(
            label=f"{role.name}",
            style=discord.ButtonStyle.secondary,
            custom_id=f"condition_{role.id}"
        )
        self.role = role
        self.parent_view = parent_view
        self.condition_type = "has"  # Default
    
    async def callback(self, interaction: discord.Interaction):
        # Toggle between "has" and "doesnt_have"
        if self.condition_type == "has":
            self.condition_type = "doesnt_have"
            self.style = discord.ButtonStyle.danger
            self.label = f"❌ {self.role.name}"
        else:
            self.condition_type = "has"
            self.style = discord.ButtonStyle.success
            self.label = f"✅ {self.role.name}"
        
        self.parent_view.condition_types[self.role.id] = self.condition_type
        await interaction.response.edit_message(view=self.parent_view)

class QuickSetupView(ui.View):
    """Quick setup view with common role connection scenarios"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        
        # Add quick setup buttons
        self.add_item(QuickSetupButton(
            "VIP Roles",
            "Give VIP role when user has supporter roles",
            self.setup_vip_roles
        ))
        self.add_item(QuickSetupButton(
            "Staff Roles",
            "Give staff role when user has staff positions",
            self.setup_staff_roles
        ))
        self.add_item(QuickSetupButton(
            "Game Roles",
            "Give game-specific roles based on other game roles",
            self.setup_game_roles
        ))
        self.add_item(QuickSetupButton(
            "Custom Rule",
            "Create a completely custom role connection rule",
            self.setup_custom_rule
        ))

class QuickSetupButton(ui.Button):
    """Button for quick setup scenarios"""
    
    def __init__(self, label: str, description: str, callback):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary
        )
        self.description = description
        self.callback_func = callback
    
    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction)

class RoleConnectionManagerView(ui.View):
    """Main view for managing all role connections"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=600)
        self.manager = manager
        self.guild = guild
        
        # Load existing connections
        self.connections = self.manager.connections_cache.get(guild.id, [])
        
        # Add action buttons
        self.add_item(ui.Button(
            label="➕ Add New Rule",
            style=discord.ButtonStyle.success,
            custom_id="add_connection"
        ))
        self.add_item(ui.Button(
            label="📋 Quick Setup",
            style=discord.ButtonStyle.primary,
            custom_id="quick_setup"
        ))
        self.add_item(ui.Button(
            label="🛡️ Protected Roles",
            style=discord.ButtonStyle.secondary,
            custom_id="protected_roles"
        ))
        
        # Add connection management select if there are connections
        if self.connections:
            self.add_item(ConnectionManageSelect(manager, guild, self.connections))

class ConnectionManageSelect(ui.Select):
    """Select to manage existing connections"""
    
    def __init__(self, manager, guild, connections):
        self.manager = manager
        self.guild = guild
        self.connections = connections
        
        options = []
        for conn in connections[:25]:  # Discord limit
            target_role = guild.get_role(conn.target_role_id)
            if target_role:
                status = "✅" if conn.enabled else "❌"
                options.append(discord.SelectOption(
                    label=f"{status} {conn.action.title()} {target_role.name}",
                    value=str(conn.id),
                    description=f"ID: {conn.id} • {len(conn.conditions)} conditions"
                ))
        
        super().__init__(
            placeholder="Manage Existing Rules",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        connection_id = int(self.values[0])
        connection = next((c for c in self.connections if c.id == connection_id), None)
        
        if connection:
            view = ConnectionActionsView(self.manager, self.guild, connection)
            target_role = self.guild.get_role(connection.target_role_id)
            
            embed = discord.Embed(
                title="🔗 Manage Connection Rule",
                description=(
                    f"**Target Role:** {target_role.mention if target_role else 'Unknown'}\n"
                    f"**Action:** {connection.action.title()}\n"
                    f"**Status:** {'✅ Enabled' if connection.enabled else '❌ Disabled'}\n"
                    f"**Logic:** {connection.logic}\n"
                    f"**Conditions:** {len(connection.conditions)}"
                ),
                color=COLORS["primary"]
            )
            
            # Show conditions
            if connection.conditions:
                cond_text = []
                for cond in connection.conditions:
                    role = self.guild.get_role(cond["role_id"])
                    if role:
                        cond_type = "HAS" if cond["type"] == "has" else "DOESN'T HAVE"
                        cond_text.append(f"• User {cond_type} {role.mention}")
                
                if cond_text:
                    embed.add_field(name="📋 Conditions", value="\n".join(cond_text), inline=False)
            
            await interaction.response.edit_message(embed=embed, view=view)

class ConnectionActionsView(ui.View):
    """View for individual connection actions"""
    
    def __init__(self, manager, guild, connection):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        self.connection = connection
        
        self.add_item(ui.Button(
            label="🔄 Toggle Enable/Disable",
            style=discord.ButtonStyle.primary,
            custom_id="toggle_connection"
        ))
        self.add_item(ui.Button(
            label="✏️ Edit Logic",
            style=discord.ButtonStyle.secondary,
            custom_id="edit_logic"
        ))
        self.add_item(ui.Button(
            label="🗑️ Delete Rule",
            style=discord.ButtonStyle.danger,
            custom_id="delete_connection"
        ))
        self.add_item(ui.Button(
            label="⬅️ Back to List",
            style=discord.ButtonStyle.secondary,
            custom_id="back_to_list"
        ))
    
    async def interaction_check(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        
        if custom_id == "toggle_connection":
            await self.manager.toggle_connection(self.guild.id, self.connection.id)
            status = "enabled" if self.connection.enabled else "disabled"
            
            await interaction.followup.send(
                embed=create_embed(
                    "Connection Updated",
                    f"Rule #{self.connection.id} has been {status}.",
                    COLORS["success"]
                ),
                ephemeral=True
            )
            # Return to main view
            await self.return_to_main_view(interaction)
            
        elif custom_id == "edit_logic":
            new_logic = "OR" if self.connection.logic == "AND" else "AND"
            await self.manager.update_connection_logic(self.guild.id, self.connection.id, new_logic)
            
            await interaction.followup.send(
                embed=create_embed(
                    "Logic Updated",
                    f"Rule #{self.connection.id} logic changed to **{new_logic}**.",
                    COLORS["success"]
                ),
                ephemeral=True
            )
            await self.return_to_main_view(interaction)
            
        elif custom_id == "delete_connection":
            await self.manager.remove_connection(self.guild.id, self.connection.id)
            
            await interaction.followup.send(
                embed=create_embed(
                    "Connection Deleted",
                    f"Rule #{self.connection.id} has been removed.",
                    COLORS["success"]
                ),
                ephemeral=True
            )
            await self.return_to_main_view(interaction)
            
        elif custom_id == "back_to_list":
            await self.return_to_main_view(interaction)
    
    async def return_to_main_view(self, interaction: discord.Interaction):
        # Load updated connections and return to main view
        await self.manager.load_connections(self.guild.id)
        view = RoleConnectionManagerView(self.manager, self.guild)
        
        connections = self.manager.connections_cache.get(self.guild.id, [])
        
        embed = discord.Embed(
            title="🔗 Role Connection System",
            description=(
                "Automatically assign or remove roles based on conditions.\n\n"
                "**How it works:**\n"
                "• Create rules that give/remove roles when conditions are met\n"
                "• Conditions: User HAS or DOESN'T HAVE specific roles\n"
                "• Logic: Combine conditions with AND/OR\n"
                "• Protected Roles: Users with these roles are exempt from all rules"
            ),
            color=COLORS["primary"]
        )
        
        if connections:
            conn_text = ""
            for i, conn in enumerate(connections[:10], 1):
                target_role = self.guild.get_role(conn.target_role_id)
                if target_role:
                    status = "✅" if conn.enabled else "❌"
                    conn_text += f"{status} {i}. {conn.action.title()} **{target_role.name}**\n"
            embed.add_field(name="Active Connections", value=conn_text or "None", inline=False)
        else:
            embed.add_field(name="Active Connections", value="None configured yet", inline=False)
        
        await interaction.message.edit(embed=embed, view=view)

class ProtectedRolesView(ui.View):
    """View for managing protected roles"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=300)
        self.manager = manager
        self.guild = guild
        
        # Add role selection buttons
        self.add_item(ui.Button(
            label="➕ Add Protected Role",
            style=discord.ButtonStyle.success,
            custom_id="add_protected"
        ))
        self.add_item(ui.Button(
            label="➖ Remove Protected Role", 
            style=discord.ButtonStyle.danger,
            custom_id="remove_protected"
        ))
        self.add_item(ui.Button(
            label="⬅️ Back to Main",
            style=discord.ButtonStyle.secondary,
            custom_id="back_to_main"
        ))
    
    async def interaction_check(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        
        if custom_id == "add_protected":
            # Create a modal for adding protected role
            modal = ProtectedRoleModal(self.manager, self.guild, "add")
            await interaction.response.send_modal(modal)
            
        elif custom_id == "remove_protected":
            # Create a modal for removing protected role
            modal = ProtectedRoleModal(self.manager, self.guild, "remove")
            await interaction.response.send_modal(modal)
            
        elif custom_id == "back_to_main":
            # Return to main view
            from cogs.role_connection_main import RoleConnectionMainView
            view = RoleConnectionMainView(self.manager, self.guild)
            
            embed = discord.Embed(
                title="🔗 Role Connection System",
                description=(
                    "**Welcome to the All-in-One Role Connection Setup!**\n\n"
                    "This new interface makes creating role rules much easier:\n"
                    "✅ **Create rules in one modal** - no more endless dropdowns\n"
                    "✅ **Multiple conditions at once** - add up to 10 conditions per rule\n"
                    "✅ **Quick setup templates** - for common scenarios\n"
                    "✅ **Live preview** - see exactly what your rule will do\n"
                    "✅ **Easy management** - edit, enable/disable, or delete rules anytime"
                ),
                color=COLORS["primary"]
            )
            
            await interaction.response.edit_message(embed=embed, view=view)

class ProtectedRoleModal(ui.Modal):
    """Modal for adding/removing protected roles"""
    
    def __init__(self, manager, guild: discord.Guild, action: str):
        title = "Add Protected Role" if action == "add" else "Remove Protected Role"
        super().__init__(title=title, timeout=300)
        self.manager = manager
        self.guild = guild
        self.action = action
        
        self.add_item(ui.TextInput(
            label="Role Name",
            placeholder="Enter the exact name of the role",
            required=True,
            style=discord.TextStyle.short,
            max_length=100
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            role_name = self.children[0].value.strip()
            role = discord.utils.get(self.guild.roles, name=role_name)
            
            if not role:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Role Not Found",
                        f"No role named '{role_name}' found in this server",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            if self.action == "add":
                await self.manager.add_protected_role(self.guild.id, role.id)
                await interaction.response.send_message(
                    embed=create_embed(
                        "✅ Protected Role Added",
                        f"{role.mention} is now protected from role connection rules",
                        COLORS["success"]
                    ),
                    ephemeral=True
                )
            else:  # remove
                await self.manager.remove_protected_role(self.guild.id, role.id)
                await interaction.response.send_message(
                    embed=create_embed(
                        "✅ Protected Role Removed",
                        f"{role.mention} is no longer protected from role connection rules",
                        COLORS["success"]
                    ),
                    ephemeral=True
                )
                
        except Exception as e:
            log_system(f"[ROLE_CONNECTION] Error in protected role modal: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Error",
                    f"An error occurred: {str(e)}",
                    COLORS["error"]
                ),
                ephemeral=True
            )

# Helper functions for quick setup
async def setup_vip_roles(interaction: discord.Interaction):
    """Quick setup for VIP roles"""
    # Implementation would depend on server-specific role names
    await interaction.response.send_message(
        embed=create_embed(
            "Quick Setup - VIP Roles",
            "This feature would automatically configure VIP role rules based on your server's role structure.",
            COLORS["info"]
        ),
        ephemeral=True
    )

async def setup_staff_roles(interaction: discord.Interaction):
    """Quick setup for staff roles"""
    await interaction.response.send_message(
        embed=create_embed(
            "Quick Setup - Staff Roles", 
            "This feature would automatically configure staff role rules based on your server's role structure.",
            COLORS["info"]
        ),
        ephemeral=True
    )

async def setup_game_roles(interaction: discord.Interaction):
    """Quick setup for game roles"""
    await interaction.response.send_message(
        embed=create_embed(
            "Quick Setup - Game Roles",
            "This feature would automatically configure game role rules based on your server's role structure.",
            COLORS["info"]
        ),
        ephemeral=True
    )

async def setup_custom_rule(interaction: discord.Interaction):
    """Launch custom rule setup"""
    # Get the manager from the parent view or client
    manager = interaction.client.get_cog("RoleConnections").manager
    from cogs.role_connection_main import EnhancedRoleConnectionModal
    modal = EnhancedRoleConnectionModal(manager, interaction.guild)
    await interaction.response.send_modal(modal)