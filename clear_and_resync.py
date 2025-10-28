"""
Clear all commands and re-sync to fix verify command grouping
Run this with: python clear_and_resync.py
"""

import discord
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv

async def clear_and_sync():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    debug_guilds = os.getenv('DEBUG_GUILDS', '').split(',')
    debug_guilds = [int(g.strip()) for g in debug_guilds if g.strip()]
    
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    
    @client.event
    async def on_ready():
        print(f"✅ Logged in as {client.user}")
        
        try:
            # Clear commands from debug guilds
            for guild_id in debug_guilds:
                guild = discord.Object(id=guild_id)
                
                # Clear all commands
                tree.clear_commands(guild=guild)
                await tree.sync(guild=guild)
                print(f"✅ Cleared commands for guild {guild_id}")
            
            print("\n✅ Commands cleared!")
            print("⚠️ Now restart your bot to re-sync with the correct structure")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await client.close()
    
    try:
        await client.start(token)
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(clear_and_sync())
