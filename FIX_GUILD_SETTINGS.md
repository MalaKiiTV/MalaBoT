# Guild-Specific Settings Fix

## Problem Identified

The Welcome and Goodbye systems are saving settings **globally** (without guild_id), which causes:
1. Settings are shared across all servers
2. Config view shows "Not configured" because it looks for guild-specific keys
3. One server's settings overwrite another server's settings

## Current Broken Keys

**Welcome System:**
- Saving: `welcome_channel_id` (global)
- Reading in config: `welcome_channel_id` (global)
- Should be: `welcome_channel_id_{guild_id}`

**Goodbye System:**
- Saving: `goodbye_channel_{guild_id}` (correct!)
- Reading in config: `goodbye_channel_{guild_id}` (correct!)

**Birthday System:**
- Saving: `birthday_channel_{guild_id}` (correct!)
- Reading in config: `birthday_channel_{guild_id}` (correct!)

**XP System:**
- Saving: `xp_channel_{guild_id}` (correct!)
- Reading in config: `xp_channel_{guild_id}` (correct!)

## Files That Need Fixing

1. `cogs/setup.py` - WelcomeSetupView class (lines ~1207-1330)
2. `cogs/welcome.py` - on_member_join event (line ~50)

## Solution

Make Welcome system use guild-specific keys like all other systems.