"""
Fix all current issues:
1. Verify cog - "Command already registered" error
2. xpadmin add/set - amount parameter issues
3. Add /xpconfig command for easy XP configuration
4. Clean up unnecessary files
"""

def fix_verify_cog_registration():
    """Fix the verify cog double registration issue"""
    
    with open('cogs/verify.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is we're adding the group twice:
    # 1. When the cog loads (class variable)
    # 2. In the setup function (bot.tree.add_command)
    
    # Remove the bot.tree.add_command line from setup
    old_setup = '''async def setup(bot: commands.Bot):
    cog = Verify(bot)
    await bot.add_cog(cog)
    # Ensure the verify group is added to the command tree
    bot.tree.add_command(cog.verify)'''
    
    new_setup = '''async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))'''
    
    content = content.replace(old_setup, new_setup)
    
    with open('cogs/verify.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed verify cog registration (removed duplicate add_command)")

def fix_xpadmin_amount_parameter():
    """Fix xpadmin amount parameter to be required for add/remove/set"""
    
    with open('cogs/xp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The issue is amount=0 as default makes it optional
    # For add/remove/set, amount should be required
    
    # Change the command signature
    old_sig = '''    async def xpadmin(self, interaction: discord.Interaction, action: str, user: discord.Member, amount: int = 0):'''
    
    new_sig = '''    async def xpadmin(self, interaction: discord.Interaction, action: str, user: discord.Member, amount: int = None):'''
    
    content = content.replace(old_sig, new_sig)
    
    # Add validation at the start of the command
    old_validation_start = '''            # Check permissions - Server Administrator or Bot Owner
            if not (interaction.user.guild_permissions.administrator or is_owner(interaction.user)):'''
    
    new_validation_start = '''            # Validate amount parameter for actions that need it
            if action in ["add", "remove", "set"] and (amount is None or amount == 0):
                embed = embed_helper.error_embed(
                    title="Missing Amount",
                    description=f"Please specify an amount for the {action} action.\\nExample: `/xpadmin {action} @user 100`"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Check permissions - Server Administrator or Bot Owner
            if not (interaction.user.guild_permissions.administrator or is_owner(interaction.user)):'''
    
    content = content.replace(old_validation_start, new_validation_start)
    
    with open('cogs/xp.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed xpadmin amount parameter validation")

def add_xpconfig_command():
    """Add /xpconfig command for easy XP configuration"""
    
    with open('cogs/xp.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where to insert the new command (after xpadmin)
    insert_pos = content.find('    async def _xpadmin_add(')
    
    if insert_pos == -1:
        print("❌ Could not find insertion point for xpconfig command")
        return False
    
    xpconfig_command = '''
    @app_commands.command(name="xpconfig", description="View and configure XP settings (Administrator only)")
    @app_commands.describe(
        setting="Setting to view or change (leave empty to view all)",
        value="New value for the setting (leave empty to view current)"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="XP per message (min)", value="xp_min"),
        app_commands.Choice(name="XP per message (max)", value="xp_max"),
        app_commands.Choice(name="XP cooldown (seconds)", value="cooldown"),
        app_commands.Choice(name="Daily bonus XP", value="daily_xp"),
        app_commands.Choice(name="Streak bonus (%)", value="streak_bonus"),
    ])
    async def xpconfig(self, interaction: discord.Interaction, setting: str = None, value: int = None):
        """View or configure XP settings."""
        try:
            # Check permissions
            if not (interaction.user.guild_permissions.administrator or is_owner(interaction.user)):
                embed = embed_helper.error_embed(
                    title="Permission Denied",
                    description="This command requires Administrator permission."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            from config.constants import (
                XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX, XP_COOLDOWN_SECONDS,
                DAILY_CHECKIN_XP, STREAK_BONUS_PERCENT
            )
            
            # If no setting specified, show all current settings
            if setting is None:
                embed = create_embed(
                    title="⚙️ Current XP Configuration",
                    description="These settings apply to all servers using this bot.",
                    color=COLORS["info"]
                )
                
                embed.add_field(
                    name="💬 Message XP",
                    value=f"**Min:** {XP_PER_MESSAGE_MIN} XP\\n**Max:** {XP_PER_MESSAGE_MAX} XP",
                    inline=True
                )
                
                embed.add_field(
                    name="⏱️ Cooldown",
                    value=f"{XP_COOLDOWN_SECONDS} seconds",
                    inline=True
                )
                
                embed.add_field(
                    name="📅 Daily Bonus",
                    value=f"{DAILY_CHECKIN_XP} XP",
                    inline=True
                )
                
                embed.add_field(
                    name="🔥 Streak Bonus",
                    value=f"{STREAK_BONUS_PERCENT}% per day",
                    inline=True
                )
                
                embed.add_field(
                    name="📝 How to Change",
                    value="Edit `config/constants.py` and restart the bot.\\n\\nExample:\\n`XP_PER_MESSAGE_MIN = 10`\\n`XP_PER_MESSAGE_MAX = 20`",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # If setting specified but no value, show current value
            if value is None:
                setting_info = {
                    "xp_min": ("Minimum XP per message", XP_PER_MESSAGE_MIN),
                    "xp_max": ("Maximum XP per message", XP_PER_MESSAGE_MAX),
                    "cooldown": ("XP cooldown", XP_COOLDOWN_SECONDS, "seconds"),
                    "daily_xp": ("Daily bonus XP", DAILY_CHECKIN_XP),
                    "streak_bonus": ("Streak bonus", STREAK_BONUS_PERCENT, "%")
                }
                
                name, current, *unit = setting_info[setting]
                unit_str = f" {unit[0]}" if unit else ""
                
                embed = create_embed(
                    title=f"⚙️ {name}",
                    description=f"**Current value:** {current}{unit_str}\\n\\nTo change this, edit `config/constants.py` and restart the bot.",
                    color=COLORS["info"]
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # If both setting and value specified, show how to change
            embed = embed_helper.info_embed(
                title="⚙️ Configuration Instructions",
                description=f"To change this setting:\\n\\n1. Edit `config/constants.py`\\n2. Find the setting and change its value\\n3. Restart the bot\\n\\n**Note:** Changes apply to all servers using this bot."
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            self.logger.error(f"Error in xpconfig command: {e}")
            await self._error_response(interaction, "Failed to show XP configuration")
    
'''
    
    # Insert the command
    content = content[:insert_pos] + xpconfig_command + content[insert_pos:]
    
    with open('cogs/xp.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Added /xpconfig command")
    return True

def cleanup_unnecessary_files():
    """Remove files that are no longer needed"""
    import os
    
    files_to_remove = [
        'fix_real_issues.py',
        'fix_verify_structure.py',
        'fix_verify_commands_final.py',
        'fix_xp_permissions_and_config.py',
        'clear_and_resync.py',
        'xpconfig_command_template.txt'
    ]
    
    removed = []
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            removed.append(file)
    
    if removed:
        print(f"✅ Removed {len(removed)} unnecessary files:")
        for file in removed:
            print(f"   • {file}")
    else:
        print("✅ No unnecessary files to remove")

def main():
    """Main execution"""
    print("🔧 Fixing all current issues...\\n")
    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("1️⃣ Fixing verify cog registration...")
    fix_verify_cog_registration()
    
    print("\\n2️⃣ Fixing xpadmin amount parameter...")
    fix_xpadmin_amount_parameter()
    
    print("\\n3️⃣ Adding /xpconfig command...")
    add_xpconfig_command()
    
    print("\\n4️⃣ Cleaning up unnecessary files...")
    cleanup_unnecessary_files()
    
    print("\\n✅ All fixes applied!")
    print("\\n📝 Summary:")
    print("   • Fixed verify cog 'already registered' error")
    print("   • Fixed xpadmin amount parameter validation")
    print("   • Added /xpconfig command to view XP settings")
    print("   • Cleaned up temporary fix files")
    print("\\n🔄 Next: Restart bot to apply changes")
    print("\\n📋 New Commands:")
    print("   • /xpconfig - View current XP settings")
    print("   • /xpconfig setting - View specific setting")
    print("   • Shows how to edit config/constants.py to change settings")

if __name__ == "__main__":
    main()