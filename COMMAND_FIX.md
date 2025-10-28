# MalaBoT Command Sync Fix

## Problem Identified

Your bot logs show:
```
discord.app_commands.errors.CommandNotFound: Application command 'help' not found
discord.app_commands.errors.CommandNotFound: Application command 'owner' not found
```

This means Discord is not recognizing the commands even though the bot says they're synced.

## Root Cause

The issue is that the bot is syncing commands, but Discord's cache is stale or the commands weren't properly cleared before resyncing. This commonly happens when:

1. Commands are modified but not properly cleared
2. The bot syncs too quickly after startup
3. Discord's API cache hasn't updated

## Solution

### Option 1: Manual Command Clear (RECOMMENDED - FASTEST)

Run this Python script to forcefully clear and resync all commands:

```python
# clear_and_sync.py
import discord
from discord.ext import commands
import asyncio
from config.settings import settings

async def clear_and_sync():
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix="/", intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        
        # Clear all global commands
        bot.tree.clear_commands(guild=None)
        print("Cleared global commands")
        
        # Clear commands from all guilds
        for guild in bot.guilds:
            bot.tree.clear_commands(guild=guild)
            await bot.tree.sync(guild=guild)
            print(f"Cleared commands from guild: {guild.name}")
        
        # Sync global commands (empty)
        await bot.tree.sync()
        print("Synced empty global commands")
        
        print("\nAll commands cleared! Now restart your bot normally.")
        await bot.close()
    
    await bot.start(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(clear_and_sync())
```

**Steps:**
1. Stop your bot
2. Run: `python clear_and_sync.py`
3. Wait for it to complete
4. Start your bot normally with `python bot.py`

### Option 2: Fix bot.py _sync_commands Method

Replace the `_sync_commands` method in bot.py with this improved version:

```python
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
```

### Option 3: Use Discord Developer Portal

1. Go to https://discord.com/developers/applications
2. Select your bot application
3. Go to "OAuth2" → "URL Generator"
4. Select scopes: `bot` and `applications.commands`
5. Copy the generated URL
6. Open it in a browser and re-authorize your bot to your server
7. This will refresh Discord's command cache

### Option 4: Add DEBUG_GUILDS to .env

Add your server ID to .env for instant command updates:

```env
DEBUG_GUILDS=YOUR_SERVER_ID_HERE
```

Replace `YOUR_SERVER_ID_HERE` with your actual Discord server ID. This makes commands sync instantly to that server instead of waiting up to 1 hour for global sync.

## Verification Steps

After applying the fix:

1. Stop the bot completely
2. Clear commands (Option 1 or manually)
3. Start the bot
4. Wait 30 seconds
5. In Discord, type `/` and you should see all commands
6. Test each command to verify they work

## Expected Commands

Your bot should have these commands:
- `/help` - Show help information
- `/ping` - Check bot latency
- `/userinfo` - User information
- `/serverinfo` - Server information
- `/about` - Bot information
- `/serverstats` - Server statistics
- `/joke` - Random joke
- `/fact` - Random fact
- `/roast` - Roast command
- `/8ball` - Magic 8-ball
- `/roll` - Roll dice
- `/coinflip` - Flip a coin
- `/owner` - Owner control panel
- `/verify` - Verification system (with subcommands)
- And more from other cogs...

## If Commands Still Don't Work

If commands still don't appear after trying all options:

1. Check bot permissions - ensure it has `applications.commands` scope
2. Check if bot is in the server
3. Verify DISCORD_TOKEN is correct in .env
4. Check Discord API status: https://discordstatus.com
5. Try kicking and re-inviting the bot with proper permissions

## Prevention

To prevent this issue in the future:

1. Always use DEBUG_GUILDS for development
2. Don't modify command names/descriptions frequently
3. Wait at least 30 seconds between bot restarts
4. Use the clear_and_sync.py script before major updates