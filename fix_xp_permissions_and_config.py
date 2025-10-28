"""
Fix XP system to be server-configurable:
1. Change xpadmin to check for Administrator permission instead of bot owner
2. Add per-server XP configuration system
3. Make bot deployable to any server with customizable settings
"""

def fix_xpadmin_permissions():
    """Change xpadmin from bot owner only to server administrator"""
    
    with open('cogs/xp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the permission check
    old_check = '''            # Check permissions
            if not is_owner(interaction.user):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command is only available to the bot owner."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return'''
    
    new_check = '''            # Check permissions - Server Administrator or Bot Owner
            if not (interaction.user.guild_permissions.administrator or is_owner(interaction.user)):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command requires Administrator permission."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return'''
    
    content = content.replace(old_check, new_check)
    
    # Update the command description
    content = content.replace(
        '@app_commands.command(name="xpadmin", description="XP administration commands (Bot Owner only)")',
        '@app_commands.command(name="xpadmin", description="XP administration commands (Administrator only)")'
    )
    
    with open('cogs/xp.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Changed xpadmin to require Administrator permission instead of Bot Owner")

def create_server_config_system():
    """Create a per-server configuration system"""
    
    # Add server_settings table to database
    db_addition = '''
    
    # Add to _create_tables method in database/models.py:
    
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS server_settings (
            guild_id INTEGER PRIMARY KEY,
            xp_per_message_min INTEGER DEFAULT 5,
            xp_per_message_max INTEGER DEFAULT 15,
            xp_cooldown_seconds INTEGER DEFAULT 60,
            daily_checkin_xp INTEGER DEFAULT 50,
            streak_bonus_percent INTEGER DEFAULT 10,
            level_up_channel_id INTEGER DEFAULT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    '''
    
    print("\n📝 To add per-server configuration:")
    print("   1. Add server_settings table to database (see instructions below)")
    print("   2. Create /xpconfig command for server admins")
    print("   3. Modify XP earning to check server settings first")
    print("\n   This allows each server to customize:")
    print("   • XP per message amount")
    print("   • XP cooldown duration")
    print("   • Daily bonus amount")
    print("   • Streak bonus percentage")
    print("   • Level up announcement channel")
    
    return db_addition

def create_xpconfig_command_template():
    """Create template for xpconfig command"""
    
    template = '''
# Add this command to cogs/xp.py:

@app_commands.command(name="xpconfig", description="Configure XP settings for this server (Administrator only)")
@app_commands.describe(
    setting="Setting to configure",
    value="New value for the setting"
)
@app_commands.choices(setting=[
    app_commands.Choice(name="XP per message (min)", value="xp_min"),
    app_commands.Choice(name="XP per message (max)", value="xp_max"),
    app_commands.Choice(name="XP cooldown (seconds)", value="cooldown"),
    app_commands.Choice(name="Daily bonus XP", value="daily_xp"),
    app_commands.Choice(name="Streak bonus (%)", value="streak_bonus"),
])
async def xpconfig(self, interaction: discord.Interaction, setting: str, value: int):
    """Configure XP settings for this server."""
    try:
        # Check permissions
        if not interaction.user.guild_permissions.administrator:
            embed = embed_helper.error_embed(
                title="Permission Denied",
                description="This command requires Administrator permission."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate value
        if value < 0:
            embed = embed_helper.error_embed(
                title="Invalid Value",
                description="Value must be positive."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update server settings in database
        conn = await self.bot.db_manager.get_connection()
        
        # Map setting to database column
        column_map = {
            "xp_min": "xp_per_message_min",
            "xp_max": "xp_per_message_max",
            "cooldown": "xp_cooldown_seconds",
            "daily_xp": "daily_checkin_xp",
            "streak_bonus": "streak_bonus_percent"
        }
        
        column = column_map[setting]
        
        # Insert or update
        await conn.execute(f"""
            INSERT INTO server_settings (guild_id, {column})
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET {column} = ?, updated_at = CURRENT_TIMESTAMP
        """, (interaction.guild.id, value, value))
        await conn.commit()
        
        # Show success
        setting_names = {
            "xp_min": "Minimum XP per message",
            "xp_max": "Maximum XP per message",
            "cooldown": "XP cooldown",
            "daily_xp": "Daily bonus XP",
            "streak_bonus": "Streak bonus percentage"
        }
        
        embed = embed_helper.success_embed(
            title="XP Settings Updated",
            description=f"**{setting_names[setting]}** has been set to **{value}**"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        self.logger.info(f"Admin {interaction.user.name} updated {setting} to {value} in {interaction.guild.name}")
        
    except Exception as e:
        self.logger.error(f"Error in xpconfig command: {e}")
        await self._error_response(interaction, "Failed to update XP settings")
'''
    
    with open('xpconfig_command_template.txt', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("\n✅ Created xpconfig_command_template.txt")
    print("   This shows how to add per-server XP configuration")

def main():
    """Main execution"""
    print("🔧 Fixing XP permissions and adding server configuration...\n")
    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("1️⃣ Fixing xpadmin permissions...")
    fix_xpadmin_permissions()
    
    print("\n2️⃣ Creating server configuration system...")
    db_addition = create_server_config_system()
    
    print("\n3️⃣ Creating xpconfig command template...")
    create_xpconfig_command_template()
    
    print("\n✅ Immediate fix applied!")
    print("   • xpadmin now works for Server Administrators")
    print("   • Bot owners can still use it")
    print("\n📝 For full per-server configuration:")
    print("   • See xpconfig_command_template.txt for implementation")
    print("   • This requires database schema update")
    print("   • Would allow each server to customize XP settings")
    print("\n🔄 Next: Restart bot to apply xpadmin permission fix")

if __name__ == "__main__":
    main()