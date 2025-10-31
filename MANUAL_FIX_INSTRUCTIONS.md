# Manual Fix Instructions - 5 Minutes

I apologize for the automation issues. Here's the **exact manual fix** - it's actually faster than debugging scripts.

## File 1: `cogs/xp.py`

### Change 1: Line 407-409 (Update describe decorator)

**Find:**
```python
       @app_commands.describe(
           user="User to reset XP for"
       )
```

**Replace with:**
```python
       @app_commands.describe(
           user="User to reset XP for (leave empty to reset ALL users)",
           confirm="Type 'yes' to confirm resetting ALL users (only needed for all reset)"
       )
```

### Change 2: Line 410 (Update function signature)

**Find:**
```python
       async def xpreset(self, interaction: discord.Interaction, user: discord.Member):
```

**Replace with:**
```python
       async def xpreset(self, interaction: discord.Interaction, user: discord.Member = None, confirm: str = None):
```

### Change 3: Line 422 (Update function body)

**Find:**
```python
               await self._xpadmin_reset(interaction, user)
           except Exception as e:
```

**Replace with:**
```python
               # If user is specified, reset single user
               if user:
                   await self._xpadmin_reset(interaction, user)
               else:
                   # Reset all users
                   await self._xpadmin_reset_all(interaction, confirm)
           except Exception as e:
```

### Change 4: After line 538 (Add new method)

**After the `_xpadmin_reset` method ends (after line 538), add this new method:**

```python
       
       async def _xpadmin_reset_all(self, interaction: discord.Interaction, confirm: str = None):
           """Reset ALL users' XP and levels."""
           try:
               # Require confirmation
               if confirm != "yes":
                   embed = embed_helper.warning_embed(
                       title="⚠️ Confirmation Required",
                       description=(
                           "This will reset **ALL users'** XP and levels to 0!\n\n"
                           "To confirm, run:\n"
                           "`/xpreset confirm:yes`\n\n"
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
```

---

## File 2: `cogs/setup.py`

### Change: Before line 1804 (Add button to XPSetupView)

**Find this (end of XPSetupView class):**
```python
           modal.on_submit = modal_callback
           await interaction.response.send_modal(modal)
   
   
   class Setup(commands.Cog):
```

**Replace with:**
```python
           modal.on_submit = modal_callback
           await interaction.response.send_modal(modal)
       
       @discord.ui.button(label="Manage Level Roles", style=ButtonStyle.success, emoji="🏆", row=2)
       async def manage_level_roles(self, interaction: discord.Interaction, button: Button):
           """Manage level role rewards"""
           await interaction.response.defer(ephemeral=True)
           
           # Get current level roles
           level_roles_data = await self.db_manager.get_setting(f"xp_level_roles_{self.guild_id}")
           
           description = "**Level Role Rewards**\n\n"
           description += "Use `/xplevelrole` commands to manage level roles:\n\n"
           description += "• `/xplevelrole action:Add level:10 role:@Role` - Add a level role\n"
           description += "• `/xplevelrole action:Remove level:10` - Remove a level role\n"
           description += "• `/xplevelrole action:List` - List all level roles\n\n"
           
           if level_roles_data:
               level_roles = {}
               for pair in level_roles_data.split(","):
                   if ":" in pair:
                       lvl, role_id = pair.split(":")
                       level_roles[int(lvl)] = int(role_id)
               
               if level_roles:
                   description += "**Currently Configured:**\n"
                   sorted_roles = sorted(level_roles.items())
                   for lvl, role_id in sorted_roles:
                       role = interaction.guild.get_role(role_id)
                       if role:
                           description += f"• Level {lvl}: {role.mention}\n"
                       else:
                           description += f"• Level {lvl}: *Role not found (ID: {role_id})*\n"
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
   
   
   class Setup(commands.Cog):
```

---

## After Making Changes:

1. **Test compilation:**
   ```bash
   python3 -m py_compile cogs/xp.py cogs/setup.py
   ```

2. **Commit and push:**
   ```bash
   git add cogs/xp.py cogs/setup.py
   git commit -m "feat: Add xpreset all and level roles button"
   git push origin main
   ```

3. **Deploy and test**

---

## Estimated Time: 5 minutes

This is much faster than debugging automation scripts. I apologize for wasting your time with the failed automation attempts!