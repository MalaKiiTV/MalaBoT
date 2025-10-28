"""
Fix duplicate commands issue
This script modifies bot.py to only sync to DEBUG_GUILDS when set (local dev)
or only sync globally when DEBUG_GUILDS is not set (production)
"""

def fix_bot_sync():
    with open('bot.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the _sync_commands method
    in_sync_method = False
    method_start = -1
    method_end = -1
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'async def _sync_commands(self):' in line:
            in_sync_method = True
            method_start = i
            indent_level = len(line) - len(line.lstrip())
            continue
        
        if in_sync_method:
            current_indent = len(line) - len(line.lstrip())
            # Check if we've left the method (dedented to same or less than method def)
            if line.strip() and current_indent <= indent_level and 'async def' in line:
                method_end = i
                break
    
    if method_start == -1:
        print("Could not find _sync_commands method")
        return False
    
    # If we didn't find the end, go to end of file
    if method_end == -1:
        method_end = len(lines)
    
    # Create new method
    new_method = '''    async def _sync_commands(self):
        """Sync slash commands to Discord (instant in debug guilds)."""
        try:
            # If DEBUG_GUILDS is set, ONLY sync to those guilds (local development)
            # This prevents duplicate commands (guild + global)
            if settings.DEBUG_GUILDS:
                self.logger.info("🔧 DEBUG MODE: Syncing only to debug guilds (no global sync)")
                for guild_id in settings.DEBUG_GUILDS:
                    try:
                        guild = discord.Object(id=guild_id)
                        self.tree.copy_global_to(guild=guild)
                        synced = await self.tree.sync(guild=guild)
                        self.logger.info(f"✅ Synced {len(synced)} commands to debug guild: {guild_id}")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to sync to debug guild {guild_id}: {e}")
            else:
                # No DEBUG_GUILDS set = Production mode = Global sync only
                self.logger.info("🌐 PRODUCTION MODE: Syncing globally")
                synced = await self.tree.sync()
                self.logger.info(f"✅ Synced {len(synced)} global commands")

        except Exception as e:
            self.logger.error(f"❌ Command sync failed: {e}")

'''
    
    # Replace the method
    new_lines = lines[:method_start] + [new_method] + lines[method_end:]
    
    # Write back
    with open('bot.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ bot.py updated successfully!")
    print("\nWhat changed:")
    print("- When DEBUG_GUILDS is set: Only syncs to those guilds (local dev)")
    print("- When DEBUG_GUILDS is NOT set: Only syncs globally (production)")
    print("\nThis prevents duplicate commands!")
    return True

if __name__ == "__main__":
    print("Fixing duplicate commands issue...\n")
    if fix_bot_sync():
        print("\n✅ Fix complete!")
        print("\nNext steps:")
        print("1. Add DEBUG_GUILDS=your_server_id to .env")
        print("2. dev.bat → Option 22 (Clear All)")
        print("3. dev.bat → Option 1 (Start Bot)")
        print("4. You'll only see commands once in your test server")
        print("5. Production (droplet) won't have DEBUG_GUILDS, so it syncs globally")
    else:
        print("\n❌ Fix failed - check bot.py manually")