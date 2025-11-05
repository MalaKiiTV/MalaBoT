"""
Loads environment variables from the .env file.
All environment-specific settings and secrets should be loaded here.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# --- Load Environment Variables ---
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- Bot Secrets ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# --- Guild Settings (for debug/dev mode) ---
DEBUG_GUILD_ID = int(os.getenv("DEBUG_GUILD_ID"))

# --- Bot Configuration ---
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ('true', '1', 't')