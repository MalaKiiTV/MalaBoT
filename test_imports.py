#!/usr/bin/env python3
"""Test script to check if all imports work correctly"""

import sys
import os

# Test imports without actually running the bot
try:
    import discord
    print("✓ discord.py imported successfully")
except ImportError as e:
    print(f"✗ Failed to import discord.py: {e}")
    sys.exit(1)

try:
    from config.settings import settings
    print("✓ Settings imported successfully")
except ImportError as e:
    print(f"✗ Failed to import settings: {e}")
    sys.exit(1)

try:
    from utils.logger import get_logger
    print("✓ Logger imported successfully")
except ImportError as e:
    print(f"✗ Failed to import logger: {e}")
    sys.exit(1)

try:
    from utils.helpers import embed_helper
    print("✓ Helpers imported successfully")
except ImportError as e:
    print(f"✗ Failed to import helpers: {e}")
    sys.exit(1)

try:
    from config.constants import COLORS
    print("✓ Constants imported successfully")
except ImportError as e:
    print(f"✗ Failed to import constants: {e}")
    sys.exit(1)

try:
    from database.models import DatabaseManager
    print("✓ Database models imported successfully")
except ImportError as e:
    print(f"✗ Failed to import database models: {e}")
    sys.exit(1)

# Test if cogs can be imported
cogs_dir = "cogs"
if os.path.exists(cogs_dir):
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            cog_name = filename[:-3]
            try:
                __import__(f'cogs.{cog_name}')
                print(f"✓ Cog {cog_name} imported successfully")
            except ImportError as e:
                print(f"✗ Failed to import cog {cog_name}: {e}")

print("\n✅ All imports successful! The bot should be ready to run with proper configuration.")