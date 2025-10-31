#!/bin/bash

echo "Applying new features to MalaBoT..."

# Create a Python script to do the work
cat > /tmp/apply_features.py << 'PYTHON_SCRIPT'
import sys

# Feature 1: Update xpreset in cogs/xp.py
print("Updating cogs/xp.py...")
with open('cogs/xp.py', 'r') as f:
    content = f.read()

# Check if already applied
if '_xpadmin_reset_all' in content:
    print("  ✓ xpreset changes already applied")
else:
    # Apply changes using simple string replacement
    # 1. Update describe
    content = content.replace(
        '       @app_commands.describe(\n           user="User to reset XP for"\n       )\n       async def xpreset(self, interaction: discord.Interaction, user: discord.Member):',
        '       @app_commands.describe(\n           user="User to reset XP for (leave empty to reset ALL users)",\n           confirm="Type \'yes\' to confirm resetting ALL users (only needed for all reset)"\n       )\n       async def xpreset(self, interaction: discord.Interaction, user: discord.Member = None, confirm: str = None):'
    )
    
    # 2. Update body
    content = content.replace(
        '               await self._xpadmin_reset(interaction, user)\n           except Exception as e:\n               self.logger.error(f"Error in xpreset command: {e}")',
        '               # If user is specified, reset single user\n               if user:\n                   await self._xpadmin_reset(interaction, user)\n               else:\n                   # Reset all users\n                   await self._xpadmin_reset_all(interaction, confirm)\n           except Exception as e:\n               self.logger.error(f"Error in xpreset command: {e}")'
    )
    
    # 3. Add new method
    insert_point = '               self.logger.info(f"Admin {interaction.user.name} reset {user.name}\'s XP")\n               \n           except Exception as e:\n               self.logger.error(f"Error resetting XP: {e}")\n               await self._error_response(interaction, "Failed to reset XP")\n       \n   \n       # xpconfig command removed - use /setup instead'
    
    new_method = '''               self.logger.info(f"Admin {interaction.user.name} reset {user.name}'s XP")
               
           except Exception as e:
               self.logger.error(f"Error resetting XP: {e}")
               await self._error_response(interaction, "Failed to reset XP")
       
       async def _xpadmin_reset_all(self, interaction: discord.Interaction, confirm: str = None):
           """Reset ALL users' XP and levels."""
           try:
               # Require confirmation
               if confirm != "yes":
                   embed = embed_helper.warning_embed(
                       title="⚠️ Confirmation Required",
                       description=(
                           "This will reset **ALL users'** XP and levels to 0!\\n\\n"
                           "To confirm, run:\\n"
                           "`/xpreset confirm:yes`\\n\\n"
                           "**This action cannot be undone!**"
                       )
                   )
                   await interaction.response.send_message(embed=embed, ephemeral=True)
                   return
               
               # Defer the response as this might take a while
               await interaction.response.defer(ephemeral=True)
               
               # Get all users with XP
               conn = await self.bot.db_manager.get_connection()
               cursor = await conn.execute(
                   "SELECT user_id FROM users WHERE xp > 0"
               )
               users = await cursor.fetchall()
               
               # Reset each user
               reset_count = 0
               for user_row in users:
                   user_id = user_row[0]
                   await self.bot.db_manager.reset_user_xp(user_id)
                   reset_count += 1
               
               embed = embed_helper.success_embed(
                   title="✅ All XP Reset",
                   description=f"Successfully reset XP for **{reset_count}** users to 0"
               )
               await interaction.followup.send(embed=embed, ephemeral=True)
               
               self.logger.info(f"Admin {interaction.user.name} reset ALL users' XP ({reset_count} users)")
               
           except Exception as e:
               self.logger.error(f"Error resetting all XP: {e}")
               await self._error_response(interaction, "Failed to reset all XP")
       
   
       # xpconfig command removed - use /setup instead'''
    
    content = content.replace(insert_point, new_method)
    
    with open('cogs/xp.py', 'w') as f:
        f.write(content)
    
    print("  ✓ Applied xpreset changes")

# Feature 2: Update setup.py
print("Updating cogs/setup.py...")
with open('cogs/setup.py', 'r') as f:
    content = f.read()

# Check if already applied
if 'manage_level_roles' in content:
    print("  ✓ Level roles button already applied")
else:
    # Add button before "class Setup"
    insert_point = '           modal.on_submit = modal_callback\n           await interaction.response.send_modal(modal)\n   \n   \n   class Setup(commands.Cog):'
    
    button_code = '''           modal.on_submit = modal_callback
           await interaction.response.send_modal(modal)
       
       @discord.ui.button(label="Manage Level Roles", style=ButtonStyle.success, emoji="🏆", row=2)
       async def manage_level_roles(self, interaction: discord.Interaction, button: Button):
           """Manage level role rewards"""
           await interaction.response.defer(ephemeral=True)
           
           # Get current level roles
           level_roles_data = await self.db_manager.get_setting(f"xp_level_roles_{self.guild_id}")
           
           description = "**Level Role Rewards**\\n\\n"
           description += "Use `/xplevelrole` commands to manage level roles:\\n\\n"
           description += "• `/xplevelrole action:Add level:10 role:@Role` - Add a level role\\n"
           description += "• `/xplevelrole action:Remove level:10` - Remove a level role\\n"
           description += "• `/xplevelrole action:List` - List all level roles\\n\\n"
           
           if level_roles_data:
               level_roles = {}
               for pair in level_roles_data.split(","):
                   if ":" in pair:
                       lvl, role_id = pair.split(":")
                       level_roles[int(lvl)] = int(role_id)
               
               if level_roles:
                   description += "**Currently Configured:**\\n"
                   sorted_roles = sorted(level_roles.items())
                   for lvl, role_id in sorted_roles:
                       role = interaction.guild.get_role(role_id)
                       if role:
                           description += f"• Level {lvl}: {role.mention}\\n"
                       else:
                           description += f"• Level {lvl}: *Role not found (ID: {role_id})*\\n"
               else:
                   description += "*No level roles configured yet.*"
           else:
               description += "*No level roles configured yet.*"
           
           embed = discord.Embed(
               title="🏆 Level Role Management",
               description=description,
               color=COLORS["xp"]
           )
           
           await interaction.followup.send(embed=embed, ephemeral=True)
   
   
   class Setup(commands.Cog):'''
    
    content = content.replace(insert_point, button_code)
    
    with open('cogs/setup.py', 'w') as f:
        f.write(content)
    
    print("  ✓ Applied level roles button")

print("\n✅ All features applied successfully!")
print("\nNext steps:")
print("1. Test compilation: python3 -m py_compile cogs/xp.py cogs/setup.py")
print("2. Commit changes: git add cogs/xp.py cogs/setup.py && git commit -m 'feat: Add xpreset all and level roles button'")
print("3. Push to GitHub: git push origin main")
print("4. Deploy on droplet and run /sync")

PYTHON_SCRIPT

# Run the Python script
python3 /tmp/apply_features.py

# Clean up
rm /tmp/apply_features.py

echo ""
echo "Done! Check the output above for any errors."