#!/usr/bin/env python3
"""Actually fix the xpreset command - for real this time"""

# Read the file
with open('cogs/xp.py', 'r') as f:
    lines = f.readlines()

# Find and fix the describe decorator
for i in range(len(lines)):
    if '           user="User to reset XP for"' in lines[i]:
        # Replace this line and add confirm parameter
        lines[i] = '           user="User to reset XP for (leave empty to reset ALL users)",\n'
        lines.insert(i+1, '           confirm="Type \'yes\' to confirm resetting ALL users (only needed for all reset)"\n')
        print(f"✓ Updated describe decorator at line {i+1}")
        break

# Find and fix the function signature  
for i in range(len(lines)):
    if 'async def xpreset(self, interaction: discord.Interaction, user: discord.Member):' in lines[i]:
        lines[i] = '       async def xpreset(self, interaction: discord.Interaction, user: discord.Member = None, confirm: str = None):\n'
        print(f"✓ Updated function signature at line {i+1}")
        break

# Find and fix the function body
for i in range(len(lines)):
    if '               await self._xpadmin_reset(interaction, user)' in lines[i]:
        # Check if we're in xpreset
        in_xpreset = False
        for j in range(max(0, i-15), i):
            if 'async def xpreset' in lines[j]:
                in_xpreset = True
                break
        
        if in_xpreset:
            # Replace with if/else
            lines[i] = '               # If user is specified, reset single user\n'
            lines.insert(i+1, '               if user:\n')
            lines.insert(i+2, '                   await self._xpadmin_reset(interaction, user)\n')
            lines.insert(i+3, '               else:\n')
            lines.insert(i+4, '                   # Reset all users\n')
            lines.insert(i+5, '                   await self._xpadmin_reset_all(interaction, confirm)\n')
            print(f"✓ Updated function body at line {i+1}")
            break

# Find where to add the new method
for i in range(len(lines)):
    if 'self.logger.info(f"Admin {interaction.user.name} reset {user.name}' in lines[i]:
        # Find the end of _xpadmin_reset
        for j in range(i+1, len(lines)):
            if 'await self._error_response(interaction, "Failed to reset XP")' in lines[j]:
                # Add new method after this line
                new_method = '''       
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
'''
                lines.insert(j+1, new_method)
                print(f"✓ Added _xpadmin_reset_all method after line {j+1}")
                break
        break

# Write back
with open('cogs/xp.py', 'w') as f:
    f.writelines(lines)

print("\n✅ xpreset changes applied!")

# Now fix setup.py
print("\nFixing cogs/setup.py...")
with open('cogs/setup.py', 'r') as f:
    lines = f.readlines()

# Find where to insert the button
for i in range(len(lines)):
    if 'class Setup(commands.Cog):' in lines[i]:
        # Insert button method before this
        button_method = '''       
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
   
   
'''
        lines.insert(i, button_method)
        print(f"✓ Added manage_level_roles button before line {i+1}")
        break

with open('cogs/setup.py', 'w') as f:
    f.writelines(lines)

print("✅ setup.py changes applied!")
print("\n🎉 All changes complete! Testing compilation...")

import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', 'cogs/xp.py', 'cogs/setup.py'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Both files compile successfully!")
else:
    print(f"❌ Compilation error:\n{result.stderr}")