import discord
from discord import app_commands, ui
from discord.ext import commands
import asyncio
from typing import List, Dict
from utils.logger import log_system
from utils.helpers import create_embed
from config.constants import COLORS
from cogs.role_connection_ui_new import (
    RoleConnectionManagerView,
    QuickSetupView
)
from cogs.role_connection_improved import (
    RoleConnectionBuilderView
)

class RoleConnectionMainView(ui.View):
    """Main entry point for role connection management"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(timeout=600)
        self.manager = manager
        self.guild = guild
        
        # Add main action buttons
        self.add_item(ui.Button(
            label="➕ Create New Rule",
            style=discord.ButtonStyle.success,
            emoji="➕",
            custom_id="create_new"
        ))
        self.add_item(ui.Button(
            label="🚀 Quick Setup Templates",
            style=discord.ButtonStyle.primary,
            emoji="🚀", 
            custom_id="quick_setup"
        ))
        self.add_item(ui.Button(
            label="📋 Manage Existing Rules",
            style=discord.ButtonStyle.secondary,
            emoji="📋",
            custom_id="manage_existing"
        ))
        self.add_item(ui.Button(
            label="🛡️ Configure Protected Roles",
            style=discord.ButtonStyle.secondary,
            emoji="🛡️",
            custom_id="protected_roles"
        ))
    
    async def interaction_check(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        
        if custom_id == "create_new":
            # Launch the improved step-by-step builder
            view = RoleConnectionBuilderView(self.manager, self.guild)
            
            embed = discord.Embed(
                title="🔗 Role Connection Builder",
                description=(
                    "Welcome to the step-by-step role connection builder!\n\n"
                    "This will guide you through creating a role rule with clear explanations "
                    "and live previews at each step."
                ),
                color=COLORS["primary"]
            )
            
            embed.add_field(
                name="📋 How It Works",
                value=(
                    "1. **Select Target Role** - Choose the role to manage\n"
                    "2. **Choose Action** - Give or remove the role\n"
                    "3. **Add Conditions** - Select roles to check for\n"
                    "4. **Set Condition Type** - When should the rule trigger?\n"
                    "5. **Choose Logic** - How do multiple conditions work?\n"
                    "6. **Review & Save** - See exactly what your rule will do"
                ),
                inline=False
            )
            
            embed.set_footer(text="Step 1 will begin below - Select your target role")
            
            await interaction.response.edit_message(embed=embed, view=view)
            # The view will handle showing step 1 automatically
            
        elif custom_id == "quick_setup":
            # Show quick setup templates
            view = QuickSetupView(self.manager, self.guild)
            
            embed = discord.Embed(
                title="🚀 Quick Setup Templates",
                description=(
                    "Choose a template to quickly set up common role connection rules. "
                    "These templates will automatically configure rules based on your server's role structure."
                ),
                color=COLORS["primary"]
            )
            
            embed.add_field(
                name="👑 VIP Roles",
                value="Automatically give VIP roles when users have supporter/donor roles",
                inline=False
            )
            embed.add_field(
                name="👨‍💼 Staff Roles", 
                value="Automatically assign staff roles based on position roles",
                inline=False
            )
            embed.add_field(
                name="🎮 Game Roles",
                value="Link game-specific roles based on other gaming roles",
                inline=False
            )
            embed.add_field(
                name="⚙️ Custom Rule",
                value="Create a completely custom rule with our easy-to-use interface",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif custom_id == "manage_existing":
            # Show existing connections management
            await self.manager.load_connections(self.guild.id)
            view = RoleConnectionManagerView(self.manager, self.guild)
            
            connections = self.manager.connections_cache.get(self.guild.id, [])
            
            embed = discord.Embed(
                title="🔗 Manage Role Connection Rules",
                description=(
                    "Here you can enable/disable, edit, or delete existing role connection rules."
                ),
                color=COLORS["primary"]
            )
            
            if connections:
                conn_text = ""
                for i, conn in enumerate(connections[:10], 1):
                    target_role = self.guild.get_role(conn.target_role_id)
                    if target_role:
                        status = "✅" if conn.enabled else "❌"
                        conn_text += f"{status} **{i}.** {conn.action.title()} {target_role.mention}\n"
                        conn_text += f"   └ {len(conn.conditions)} condition(s) • {conn.logic} logic\n"
                
                embed.add_field(name="📋 Active Rules", value=conn_text, inline=False)
                embed.add_field(
                    name="💡 Tip",
                    value="Select a rule from the dropdown below to manage it, or use the buttons to create new rules.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📋 No Rules Found",
                    value="You haven't created any role connection rules yet. Use the buttons below to get started!",
                    inline=False
                )
            
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif custom_id == "protected_roles":
            # Launch protected roles configuration
            await self.setup_protected_roles(interaction)
    
    async def setup_protected_roles(self, interaction: discord.Interaction):
        """Setup protected roles configuration"""
        from cogs.role_connection_ui_new import ProtectedRolesView
        
        await self.manager.load_protected_roles(self.guild.id)
        view = ProtectedRolesView(self.manager, self.guild)
        
        protected_roles = self.manager.protected_roles_cache.get(self.guild.id, [])
        
        embed = discord.Embed(
            title="🛡️ Protected Roles Configuration",
            description=(
                "Users with protected roles are exempt from all role connection rules. "
                "This prevents automatic role assignment/removal for important roles."
            ),
            color=COLORS["primary"]
        )
        
        if protected_roles:
            protected_text = ""
            for role_id in protected_roles:
                role = self.guild.get_role(role_id)
                if role:
                    protected_text += f"• {role.mention}\n"
            
            embed.add_field(name="🛡️ Current Protected Roles", value=protected_text, inline=False)
        else:
            embed.add_field(
                name="🛡️ No Protected Roles",
                value="No roles are currently protected. Add roles below to exempt them from automated rules.",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=view)

# Enhanced Modal with better handling
class EnhancedRoleConnectionModal(ui.Modal):
    """Enhanced modal with improved validation and preview"""
    
    def __init__(self, manager, guild: discord.Guild):
        super().__init__(title="🔗 Create Role Connection Rule", timeout=600)
        self.manager = manager
        self.guild = guild
        
        # Get role options
        roles = [r for r in guild.roles if r.name != "@everyone"]
        self.role_options = [
            discord.SelectOption(
                label=role.name[:25],
                value=str(role.id),
                description=f"ID: {role.id}"
            ) for role in roles[:25]
        ]
        
        # Target role selection
        self.add_item(ui.TextInput(
            label="Target Role Name",
            placeholder="Enter the exact name of the role to give/remove",
            required=True,
            style=discord.TextStyle.short,
            max_length=100
        ))
        
        # Action selection
        self.add_item(ui.TextInput(
            label="Action (give/remove)",
            placeholder="Type 'give' or 'remove'",
            required=True,
            style=discord.TextStyle.short,
            max_length=10
        ))
        
        # Condition roles (comma separated)
        self.add_item(ui.TextInput(
            label="Condition Roles",
            placeholder="Enter role names separated by commas",
            required=True,
            style=discord.TextStyle.paragraph,
            max_length=1000
        ))
        
        # Condition type
        self.add_item(ui.TextInput(
            label="Condition Type",
            placeholder="Type 'has' or 'doesnt_have'",
            required=True,
            style=discord.TextStyle.short,
            max_length=15
        ))
        
        # Logic operator
        self.add_item(ui.TextInput(
            label="Logic (AND/OR)",
            placeholder="Type 'AND' or 'OR'",
            required=True,
            style=discord.TextStyle.short,
            max_length=5
        ))
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse and validate inputs
            target_role_name = self.children[0].value.strip()
            action = self.children[1].value.strip().lower()
            condition_names = [name.strip() for name in self.children[2].value.split(',')]
            condition_type = self.children[3].value.strip().lower()
            logic = self.children[4].value.strip().upper()
            
            # Validate action
            if action not in ['give', 'remove']:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Invalid Action",
                        "Action must be either 'give' or 'remove'",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            # Validate condition type
            if condition_type not in ['has', 'doesnt_have']:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Invalid Condition Type",
                        "Condition type must be either 'has' or 'doesnt_have'",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            # Validate logic
            if logic not in ['AND', 'OR']:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Invalid Logic",
                        "Logic must be either 'AND' or 'OR'",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            # Find target role
            target_role = discord.utils.get(self.guild.roles, name=target_role_name)
            if not target_role:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Target Role Not Found",
                        f"No role named '{target_role_name}' found in this server",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            # Find condition roles
            condition_roles = []
            missing_roles = []
            
            for role_name in condition_names:
                role = discord.utils.get(self.guild.roles, name=role_name)
                if role:
                    condition_roles.append(role)
                else:
                    missing_roles.append(role_name)
            
            if missing_roles:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ Condition Roles Not Found",
                        f"The following roles were not found: {', '.join(missing_roles)}",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            if not condition_roles:
                await interaction.response.send_message(
                    embed=create_embed(
                        "❌ No Valid Condition Roles",
                        "At least one valid condition role is required",
                        COLORS["error"]
                    ),
                    ephemeral=True
                )
                return
            
            # Build conditions
            conditions = []
            for role in condition_roles:
                conditions.append({
                    "type": condition_type,
                    "role_id": role.id
                })
            
            # Save the connection
            connection_id = await self.manager.add_connection(
                self.guild.id,
                target_role.id,
                action,
                conditions,
                logic
            )
            
            # Create success embed with preview
            embed = discord.Embed(
                title="✅ Role Connection Rule Created",
                color=COLORS["success"]
            )
            
            embed.add_field(
                name="🎯 Target Role",
                value=f"{target_role.mention}",
                inline=True
            )
            
            embed.add_field(
                name="⚡ Action",
                value=f"**{action.title()}** the role",
                inline=True
            )
            
            embed.add_field(
                name="🧠 Logic",
                value=f"**{logic}** (User must meet {logic.lower()} conditions)",
                inline=True
            )
            
            condition_text = []
            for role in condition_roles:
                condition_text.append(f"• User **{condition_type.upper()}** {role.mention}")
            
            embed.add_field(
                name="📋 Conditions",
                value="\n".join(condition_text),
                inline=False
            )
            
            embed.add_field(
                name="💡 What This Does",
                value=(
                    f"When a user **{condition_type.upper()}** {len(condition_roles)} specified role(s), "
                    f"the bot will automatically **{action}** them the {target_role.mention} role."
                ),
                inline=False
            )
            
            embed.add_field(
                name="🔧 Management",
                value=(
                    f"Use `/setup` → **Role Connections** → **Manage Existing Rules** "
                    f"to edit or delete this rule later.\n\n"
                    f"Rule ID: `{connection_id}`"
                ),
                inline=False
            )
            
            embed.set_footer(text="Rule is now active and will be applied automatically")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            log_system(f"[ROLE_CONNECTION] Error in modal submission: {e}", level="error")
            await interaction.response.send_message(
                embed=create_embed(
                    "❌ Unexpected Error",
                    f"An error occurred while creating the rule: {str(e)}",
                    COLORS["error"]
                ),
                ephemeral=True
            )