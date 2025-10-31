#!/usr/bin/env python3
"""Direct file editing - no string matching, just line numbers"""

# Fix cogs/xp.py
print("Fixing cogs/xp.py...")
with open('cogs/xp.py', 'r') as f:
    lines = f.readlines()

# Change 1: Line 408 - add confirm parameter to describe
lines[407] = '       @app_commands.describe(\n'
lines[408] = '           user="User to reset XP for (leave empty to reset ALL users)",\n'
lines.insert(409, '           confirm="Type \'yes\' to confirm resetting ALL users (only needed for all reset)"\n')

# Change 2: Line 410 (now 411 after insert) - update function signature
lines[410] = '       async def xpreset(self, interaction: discord.Interaction, user: discord.Member = None, confirm: str = None):\n'

# Change 3: Line 422 (now 423) - update function body
# Find the line with "await self._xpadmin_reset(interaction, user)"
for i in range(410, 430):
    if 'await self._xpadmin_reset(interaction, user)' in lines[i] and 'if user' not in lines[i-1]:
        lines[i] = '               # If user is specified, reset single user\n'
        lines.insert(i+1, '               if user:\n')
        lines.insert(i+2, '                   await self._xpadmin_reset(interaction, user)\n')
        lines.insert(i+3, '               else:\n')
        lines.insert(i+4, '                   # Reset all users\n')
        lines.insert(i+5, '                   await self._xpadmin_reset_all(interaction, confirm)\n')
        print(f"  ✓ Updated function body at line {i}")
        break

# Change 4: Add new method after _xpadmin_reset
# Find the end of _xpadmin_reset method
for i in range(len(lines)):
    if 'self.logger.info(f"Admin {interaction.user.name} reset {user.name}' in lines[i]:
        # Find the end
        for j in range(i+1, len(lines)):
            if 'await self._error_response(interaction, "Failed to reset XP")' in lines[j]:
                # Insert new method after this line
                new_method = [
                    '       \n',
                    '       async def _xpadmin_reset_all(self, interaction: discord.Interaction, confirm: str = None):\n',
                    '           """Reset ALL users\' XP and levels."""\n',
                    '           try:\n',
                    '               # Require confirmation\n',
                    '               if confirm != "yes":\n',
                    '                   embed = embed_helper.warning_embed(\n',
                    '                       title="⚠️ Confirmation Required",\n',
                    '                       description=(\n',
                    '                           "This will reset **ALL users\'** XP and levels to 0!\\n\\n"\n',
                    '                           "To confirm, run:\\n"\n',
                    '                           "`/xpreset confirm:yes`\\n\\n"\n',
                    '                           "**This action cannot be undone!**"\n',
                    '                       )\n',
                    '                   )\n',
                    '                   await interaction.response.send_message(embed=embed, ephemeral=True)\n',
                    '                   return\n',
                    '               \n',
                    '               # Defer the response as this might take a while\n',
                    '               await interaction.response.defer(ephemeral=True)\n',
                    '               \n',
                    '               # Get all users with XP\n',
                    '               conn = await self.bot.db_manager.get_connection()\n',
                    '               cursor = await conn.execute(\n',
                    '                   "SELECT user_id FROM users WHERE xp > 0"\n',
                    '               )\n',
                    '               users = await cursor.fetchall()\n',
                    '               \n',
                    '               # Reset each user\n',
                    '               reset_count = 0\n',
                    '               for user_row in users:\n',
                    '                   user_id = user_row[0]\n',
                    '                   await self.bot.db_manager.reset_user_xp(user_id)\n',
                    '                   reset_count += 1\n',
                    '               \n',
                    '               embed = embed_helper.success_embed(\n',
                    '                   title="✅ All XP Reset",\n',
                    '                   description=f"Successfully reset XP for **{reset_count}** users to 0"\n',
                    '               )\n',
                    '               await interaction.followup.send(embed=embed, ephemeral=True)\n',
                    '               \n',
                    '               self.logger.info(f"Admin {interaction.user.name} reset ALL users\' XP ({reset_count} users)")\n',
                    '               \n',
                    '           except Exception as e:\n',
                    '               self.logger.error(f"Error resetting all XP: {e}")\n',
                    '               await self._error_response(interaction, "Failed to reset all XP")\n',
                ]
                for line in reversed(new_method):
                    lines.insert(j+1, line)
                print(f"  ✓ Added _xpadmin_reset_all method after line {j}")
                break
        break

with open('cogs/xp.py', 'w') as f:
    f.writelines(lines)

print("✅ cogs/xp.py updated!")

# Fix cogs/setup.py
print("\nFixing cogs/setup.py...")
with open('cogs/setup.py', 'r') as f:
    lines = f.readlines()

# Find "class Setup(commands.Cog):" and insert button before it
for i in range(len(lines)):
    if 'class Setup(commands.Cog):' in lines[i]:
        button_lines = [
            '       \n',
            '       @discord.ui.button(label="Manage Level Roles", style=ButtonStyle.success, emoji="🏆", row=2)\n',
            '       async def manage_level_roles(self, interaction: discord.Interaction, button: Button):\n',
            '           """Manage level role rewards"""\n',
            '           await interaction.response.defer(ephemeral=True)\n',
            '           \n',
            '           # Get current level roles\n',
            '           level_roles_data = await self.db_manager.get_setting(f"xp_level_roles_{self.guild_id}")\n',
            '           \n',
            '           description = "**Level Role Rewards**\\n\\n"\n',
            '           description += "Use `/xplevelrole` commands to manage level roles:\\n\\n"\n',
            '           description += "• `/xplevelrole action:Add level:10 role:@Role` - Add a level role\\n"\n',
            '           description += "• `/xplevelrole action:Remove level:10` - Remove a level role\\n"\n',
            '           description += "• `/xplevelrole action:List` - List all level roles\\n\\n"\n',
            '           \n',
            '           if level_roles_data:\n',
            '               level_roles = {}\n',
            '               for pair in level_roles_data.split(","):\n',
            '                   if ":" in pair:\n',
            '                       lvl, role_id = pair.split(":")\n',
            '                       level_roles[int(lvl)] = int(role_id)\n',
            '               \n',
            '               if level_roles:\n',
            '                   description += "**Currently Configured:**\\n"\n',
            '                   sorted_roles = sorted(level_roles.items())\n',
            '                   for lvl, role_id in sorted_roles:\n',
            '                       role = interaction.guild.get_role(role_id)\n',
            '                       if role:\n',
            '                           description += f"• Level {lvl}: {role.mention}\\n"\n',
            '                       else:\n',
            '                           description += f"• Level {lvl}: *Role not found (ID: {role_id})*\\n"\n',
            '               else:\n',
            '                   description += "*No level roles configured yet.*"\n',
            '           else:\n',
            '               description += "*No level roles configured yet.*"\n',
            '           \n',
            '           embed = discord.Embed(\n',
            '               title="🏆 Level Role Management",\n',
            '               description=description,\n',
            '               color=COLORS["xp"]\n',
            '           )\n',
            '           \n',
            '           await interaction.followup.send(embed=embed, ephemeral=True)\n',
            '   \n',
            '   \n',
        ]
        for line in reversed(button_lines):
            lines.insert(i, line)
        print(f"  ✓ Added manage_level_roles button before line {i}")
        break

with open('cogs/setup.py', 'w') as f:
    f.writelines(lines)

print("✅ cogs/setup.py updated!")

# Test compilation
print("\nTesting compilation...")
import subprocess
result = subprocess.run(['python3', '-m', 'py_compile', 'cogs/xp.py', 'cogs/setup.py'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ Both files compile successfully!")
    print("\n🎉 ALL DONE! Ready to commit and push.")
else:
    print(f"❌ Compilation error:\n{result.stderr}")
    print("\nRestoring backup...")
    import shutil
    shutil.copy('cogs/xp.py.backup', 'cogs/xp.py')
    print("Backup restored. Please check the error.")