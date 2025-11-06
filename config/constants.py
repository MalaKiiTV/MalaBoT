"""
Constants and configuration values for MalaBoT.
Contains XP tables, colors, embed settings, and other static data.
"""

# Embed Color Scheme
COLORS = {
    "success": 0x00FF00,  # Green
    "warning": 0xFFAA00,  # Orange/Yellow
    "error": 0xFF0000,  # Red
    "info": 0x0099FF,  # Blue
    "primary": 0x7289DA,  # Discord blurple
    "roast": 0xFF6B35,  # Orange/Red for roast system
    "birthday": 0xFF69B4,  # Pink for birthdays
    "welcome": 0x00D4AA,  # Teal for welcomes
    "xp": 0x9B59B6,  # Purple for XP system
}

# XP System Configuration
XP_PER_MESSAGE = 10  # Fixed XP per message (no range)
XP_PER_REACTION = 2  # Fixed XP per reaction received
XP_PER_VOICE_MINUTE = 5  # Fixed XP per minute in voice
XP_COOLDOWN_SECONDS = 60
DAILY_CHECKIN_XP = 50
STREAK_BONUS_PERCENT = 10
ROAST_LEADERBOARD_LIMIT = 10

# XP Level Requirements (cumulative XP needed)
XP_TABLE = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    6: 1000,
    7: 1400,
    8: 1900,
    9: 2500,
    10: 3200,
    11: 4000,
    12: 5000,
    13: 6200,
    14: 7600,
    15: 9200,
    16: 11000,
    17: 13000,
    18: 15000,
    19: 17000,
    20: 20000,
    25: 30000,
    30: 45000,
    35: 65000,
    40: 90000,
    45: 120000,
    50: 160000,
}

# Roast XP Configuration
ROAST_XP_MIN = 5
ROAST_XP_MAX = 15
ROAST_MAX_LEVEL = 10

# Roast XP Table for Bot Levels
ROAST_XP_TABLE = {
    1: 0,
    2: 50,
    3: 150,
    4: 300,
    5: 500,
    6: 800,
    7: 1200,
    8: 1800,
    9: 2600,
    10: 3600,
}

# Roast Titles (bot progression)
ROAST_TITLES = {
    1: "Newbie Roaster",
    2: "Sassy Bot",
    3: "Sharp Tongue",
    4: "Burn Master",
    5: "Fire Brand",
    6: "Inferno Speaker",
    7: "Dragon's Breath",
    8: "Hellfire Roaster",
    9: "Legendary Burn",
    10: "Roast God",
}

# Birthday System Configuration
DEFAULT_BIRTHDAY_POST_TIME = "08:00 AM"
DEFAULT_TIMEZONE = "UTC-6"
BIRTHDAY_ROLE_NAME = "Birthday 🎂"
BIRTHDAY_CHECK_INTERVAL_HOURS = 1

# Welcome System Configuration
DEFAULT_WELCOME_TITLE = "👋 Welcome to the server!"
DEFAULT_WELCOME_MESSAGE = "We're glad you're here, {member.mention}!"
DEFAULT_WELCOME_IMAGE = None

# Goodbye System Configuration
DEFAULT_GOODBYE_TITLE = "👋 Goodbye!"
DEFAULT_GOODBYE_MESSAGE = "{member.name} has left the server. We'll miss you!"
DEFAULT_GOODBYE_IMAGE = None

# Moderation System Configuration
DELETE_LOG_LIMIT = 10
MAX_MESSAGES_DELETE = 100

# Help System Configuration
HELP_EMBED_COLOR = COLORS["primary"]
HELP_EMBED_TITLE = "🤖 MalaBoT Command List"
HELP_FOOTER = "MalaBoT • Multifunctional Discord Bot"

# Bot Status Messages
STARTUP_MESSAGES = [
    "🟢 MalaBoT is now Locked in!",
    "🚀 MalaBoT is ready to roll!",
    "⚡ MalaBoT is online and kicking!",
    "🎯 MalaBoT locked and loaded!",
]

# Error Messages
ERROR_MESSAGES = {
    "permission_denied": "❌ You don't have permission to use this command.",
    "cooldown_active": "⏱️ Please wait before using this command again.",
    "invalid_user": "❌ Invalid user specified.",
    "invalid_channel": "❌ Invalid channel specified.",
    "database_error": "❌ A database error occurred. Please try again later.",
    "api_error": "❌ An external API error occurred. Please try again later.",
    "not_found": "❌ The requested resource was not found.",
    "invalid_syntax": "❌ Invalid command syntax. Use `/help` for assistance.",
}

# Success Messages
SUCCESS_MESSAGES = {
    "command_complete": "✅ Command completed successfully.",
    "data_saved": "✅ Data saved successfully.",
    "settings_updated": "✅ Settings updated successfully.",
    "user_updated": "✅ User data updated successfully.",
}

# Level Role Map (server owners should customize these)
# Format: level: role_name_or_id
LEVEL_ROLE_MAP = {
    1: None,  # Starting level, no role
    5: "Level 5",
    10: "Level 10",
    15: "Level 15",
    20: "Level 20",
    25: "Level 25",
    30: "Level 30",
    35: "Level 35",
    40: "Level 40",
    45: "Level 45",
    50: "Level 50+",
}

# Permission Levels
PERMISSION_LEVELS = {
    "OWNER": 100,
    "ADMIN": 80,
    "MODERATOR": 60,
    "MEMBER": 20,
    "EVERYONE": 0,
}

# Database Configuration
DATABASE_BACKUP_INTERVAL_HOURS = 24
DATABASE_MAX_BACKUPS = 10
LOG_MAX_SIZE_MB = 10
LOG_RETENTION_DAYS = 30
BACKUP_RETENTION_DAYS = 30

# Command Categories for Help System
COMMAND_CATEGORIES = {
    "🎮 Fun": ["joke", "fact", "roast", "8ball", "roll", "coinflip"],
    "⚙️ Utility": ["help", "ping", "userinfo", "serverinfo", "about", "serverstats"],
    "🎂 Birthdays": ["bday"],
    "🏆 XP": ["xp rank", "xp leaderboard", "xp checkin", "xp add", "xp remove", "xp set", "xp reset"],
    "🛡️ Admin": ["delete", "kick", "ban", "mute", "unmute", "setup"],
    "✅ Verification": ["verify activision", "verify review"],
    "📋 Appeals": ["appeal submit", "appeal review"],
    "👑 Owner": ["owner", "clear-commands"],
}

# Jokes Database (sample jokes)
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why can't a bicycle stand up by itself? It's two tired!",
    "What do you call a fake noodle? An impasta!",
    "Why did the math book look sad? Because it had too many problems!",
    "What do you call cheese that isn't yours? Nacho cheese!",
]

# Facts Database (sample facts)
FACTS = [
    "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!",
    "A group of flamingos is called a 'flamboyance'.",
    "Octopuses have three hearts and blue blood.",
    "Bananas are berries, but strawberries aren't!",
    "A day on Venus is longer than its year.",
    "The shortest war in history lasted 38 minutes (Anglo-Zanzibar War, 1896).",
    "A group of crows is called a 'murder'.",
    "Sharks have been around longer than trees!",
]

# Roasts Database (sample roasts)
ROASTS = [
    "You're like a software update - nobody wants you but you keep popping up anyway!",
    "I'd agree with you but then we'd both be wrong.",
    "You're living proof that even bots have better social skills than some people!",
    "If ignorance was bliss, you'd be the happiest person alive!",
    "You're the reason God created the middle finger.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "You're not stupid, you're just possessed by a slow ghost.",
    "If I wanted to kill myself I'd climb your ego and jump to your IQ.",
    "You're about as useful as a white crayon.",
    "I'd call you a tool, but that would be an insult to tools.",
]

# Command Cooldowns (in seconds)
COMMAND_COOLDOWNS = {
    "joke": 5,
    "fact": 5,
    "roast": 10,
    "ping": 10,
}

# System Messages
SYSTEM_MESSAGES = {
    "startup_verification": "=== STARTUP VERIFICATION REPORT ===",
    "database_integrity": "=== DATABASE INTEGRITY REPORT ===",
    "daily_digest": "=== DAILY DIGEST REPORT ===",
    "watchdog_report": "=== WATCHDOG REPORT ===",
    "audit_cleanup": "=== AUDIT LOG CLEANUP ===",
}

# Time Formats
TIME_FORMATS = {
    "12hour": "%I:%M %p",
    "24hour": "%H:%M",
    "date": "%Y-%m-%d",
    "datetime": "%Y-%m-%d %H:%M:%S",
    "iso": "%Y-%m-%dT%H:%M:%SZ",
}

# File Paths
DATA_DIR = "data"
LOGS_DIR = "data/logs"
BACKUPS_DIR = "backups"
DATABASE_DIR = "database"
COGS_DIR = "cogs"
UTILS_DIR = "utils"

# Bot Limits
MAX_MESSAGE_LENGTH = 2000
MAX_EMBED_DESCRIPTION = 2048
MAX_EMBED_TITLE = 256
MAX_EMBED_FIELDS = 25
MAX_EMBED_FIELD_VALUE = 1024