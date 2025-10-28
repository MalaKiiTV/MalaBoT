"""
This file contains the fixed _sync_commands method for bot.py
Replace the existing _sync_commands method (around line 582) with this version.
"""

async def _sync_commands(self):
    """Sync slash commands to Discord (instant in debug guilds)."""
    try:
        self.logger.info("Starting command sync...")
        
        # Clear existing commands first to ensure clean sync
        self.tree.clear_commands(guild=None)
        self.logger.info("Cleared global commands from tree")
        
        # Sync to debug guilds first (for instant updates)
        if settings.DEBUG_GUILDS:
            for guild_id in settings.DEBUG_GUILDS:
                try:
                    guild = discord.Object(id=guild_id)
                    # Clear guild-specific commands
                    self.tree.clear_commands(guild=guild)
                    # Copy global commands to guild
                    self.tree.copy_global_to(guild=guild)
                    # Sync to guild
                    synced = await self.tree.sync(guild=guild)
                    self.logger.info(f"✅ Synced {len(synced)} commands to debug guild: {guild_id}")
                    for cmd in synced:
                        self.logger.info(f"  - /{cmd.name}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to sync to debug guild {guild_id}: {e}")
        
        # Global sync (takes up to 1 hour to propagate)
        synced = await self.tree.sync()
        self.logger.info(f"✅ Slash commands force-resynced successfully.")
        self.logger.info(f"🌐 Global commands synced: {len(synced)} commands")
        for cmd in synced:
            self.logger.info(f"  - /{cmd.name}")
        
    except Exception as e:
        self.logger.error(f"❌ Command sync failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())