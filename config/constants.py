"""
This file contains static constants for the MalaBoT.
It should not contain any secrets or environment-specific settings.
"""

import discord

# --- Bot-wide constants ---
XP_PER_MESSAGE_MIN = 15
XP_PER_MESSAGE_MAX = 25
XP_COOLDOWN_SECONDS = 60

# --- Color constants for embeds ---
class COLORS:
    primary = discord.Color.blue()
    success = discord.Color.green()
    error = discord.Color.red()
    warning = discord.Color.orange()
    info = discord.Color.purple()
    gold = discord.Color.gold()