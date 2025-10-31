#!/usr/bin/env python3
"""Safe fix using targeted string replacement"""

# Read xp.py
with open('cogs/xp.py', 'r') as f:
    content = f.read()

print("Fixing cogs/xp.py...")

# Fix 1: Update describe decorator - find exact match
old_describe = '''       @app_commands.command(name="xpreset", description="Reset user XP to 0 (Server Owner only)")
       @app_commands.describe(
           user="User to reset XP for"
       )
       async def xpreset(self, interaction: discord.Interaction, user: discord.Member):'''

new_describe = '''       @app_commands.command(name="xpreset", description="Reset user XP to 0 (Server Owner only)")
       @app_commands.describe(
           user="User to reset XP for (leave empty to reset ALL users)",
           confirm="Type 'yes' to confirm resetting ALL users (only needed for all reset)"
       )
       async def xpreset(self, interaction: discord.Interaction, user: discord.Member = None, confirm: str = None):'''

if old_describe in content:
    content = content.replace(old_describe, new_describe)
    print("  ✓ Updated describe and function signature")
else:
    print("  ✗ Could not find describe pattern")

# Fix 2: Update function body
old_body = '''                   return
               
               await self._xpadmin_reset(interaction, user)
           except Exception as e:
               self.logger.error(f"Error in xpreset command: {e}")'''

new_body = '''                   return
               
               # If user is specified, reset single user
               if user:
                   await self._xpadmin_reset(interaction, user)
               else:
                   # Reset all users
                   await self._xpadmin_reset_all(interaction, confirm)
           except Exception as e:
               self.logger.error(f"Error in xpreset command: {e}")'''

if old_body in content:
    content = content.replace(old_body, new_body)
    print("  ✓ Updated function body")
else:
    print("  ✗ Could not find body pattern")

# Fix 3: Add new method
old_end = '''               self.logger.info(f"Admin {interaction.user.name} reset {user.name}'s XP")
               
           except Exception as e:
               self.logger.error(f"Error resetting XP: {e}")
               await self._error_response(interaction, "Failed to reset XP")
       
   
       # xpconfig command removed - use /setup instead'''

new_end = '''               self.logger.info(f"Admin {interaction.user.name} reset {user.name}'s XP")
               
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

if old_end in content:
    content = content.replace(old_end, new_end)
    print("  ✓ Added _xpadmin_reset_all method")
else:
    print("  ✗ Could not find end pattern")

# Write back
with open('cogs/xp.py', 'w') as f:
    f.write(content)

print("✅ cogs/xp.py updated!")

# Fix setup.py
print("\nFixing cogs/setup.py...")
with open('cogs/setup.py', 'r') as f:
    content = f.read()

old_setup = '''           modal.on_submit = modal_callback
           await interaction.response.send_modal(modal)
   
   
   class Setup(commands.Cog):'''

new_setup = '''           modal.on_submit = modal_callback
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

if old_setup in content:
    content = content.replace(old_setup, new_setup)
    print("  ✓ Added manage_level_roles button")
else:
    print("  ✗ Could not find setup pattern")

with open('cogs/setup.py', 'w') as f:
    f.write(content)

print("✅ cogs/setup.py updated!")

# Test compilation
print("\nTesting compilation...")
import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', 'cogs/xp.py', 'cogs/setup.py'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Both files compile successfully!")
    print("\n🎉 ALL DONE! Changes are ready.")
else:
    print(f"❌ Compilation error:\n{result.stderr}")