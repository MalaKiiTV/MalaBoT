# MalaBoT Deployment Guide

## Prerequisites
- Python 3.8 or higher
- A Discord bot token from the Discord Developer Portal
- Git (for updates)

## Initial Setup

1. Extract the contents of this ZIP file to your desired location

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the bot:
   - Copy `.env.example` to `.env`
   - Edit `.env` and set your actual Discord bot token in the `DISCORD_TOKEN` field
   - Set your Discord user ID in the `OWNER_IDS` field (for owner-only commands)
   - Adjust other settings as needed

5. Run the bot:
   ```bash
   python bot.py
   ```

## Important Configuration Notes

The bot will not start without proper configuration. You must create a `.env` file with at least the following settings:
- `DISCORD_TOKEN`: Your actual Discord bot token (not the example value)
- `OWNER_IDS`: Your Discord user ID (not the example value)

Failure to set these values will result in startup errors.

## File Structure
```
malabot/
├── bot.py                 # Main bot entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── update.bat            # Windows update script
├── update_droplet.sh     # Linux droplet update script
├── DEPLOYMENT_GUIDE.md   # This file
├── config/
│   ├── settings.py       # Bot configuration
│   └── constants.py      # Constants and categories
├── cogs/
│   ├── utility.py        # Utility commands
│   ├── fun.py            # Entertainment commands
│   ├── xp.py             # XP system
│   ├── birthdays.py      # Birthday system
│   ├── moderation.py     # Moderation tools
│   ├── welcome.py        # Welcome system
│   └── owner.py          # Owner controls
├── database/
│   └── models.py         # Database models and manager
├── utils/
│   ├── logger.py         # Logging system
│   └── helpers.py        # Helper functions
└── data/
    ├── logs/             # Log files
    ├── backups/          # Database backups
    └── flags/            # System flags
```

## Discord Bot Configuration

1. In the Discord Developer Portal:
   - Enable "Server Members Intent"
   - Enable "Message Content Intent"
   - Set bot permissions to "Administrator" for full functionality

2. Add the bot to your server using the OAuth2 URL generator with the required permissions

## Environment Variables (.env file)

- `DISCORD_TOKEN`: Your bot's token from Discord Developer Portal
- `OWNER_IDS`: Comma-separated list of Discord user IDs who will have owner permissions
- `DATABASE_PATH`: Path to the SQLite database file (default: "database/bot.db")
- `LOG_LEVEL`: Logging level (default: "INFO")

## Update Scripts

### Windows (update.bat)
This script will:
- Gracefully stop the bot
- Pull latest changes from the repository
- Clear caches and logs
- Update dependencies
- Restart the bot
- Send an online notification to the configured channel

### Linux Droplet (update_droplet.sh)
This script will:
- Gracefully stop the bot
- Pull latest changes from the repository
- Clear caches and logs
- Update dependencies
- Restart the bot in the background
- Send an online notification to the configured channel

## Commands Overview

### Public Commands (Available to Everyone)
- `/help` - Shows all available commands organized by category
- `/ping` - Check bot latency and uptime
- `/userinfo [user]` - Get detailed information about a user
- `/serverinfo` - Get detailed information about the server
- `/about` - Get information about the bot
- `/serverstats` - Get comprehensive server statistics
- `/joke` - Get a random joke with cooldown
- `/fact` - Get a random interesting fact with cooldown
- `/roast [user]` - Get roasted by the bot
- `/8ball <question>` - Ask the magic 8-ball a question
- `/roll [sides]` - Roll a die with specified number of sides (default 6)
- `/coinflip` - Flip a coin
- `/xp rank [user]` - Check XP and level information
- `/xp leaderboard` - View server XP rankings
- `/bday set` - Set your birthday
- `/bday view` - View your birthday
- `/bday list` - List all server birthdays
- `/bday next` - View upcoming birthdays

### Admin Commands (Require Server Admin Permissions)
- `/delete last10` - Delete last 10 messages
- `/delete last50` - Delete last 50 messages
- `/delete all` - Delete all messages (clone channel)
- `/delete logs` - View moderation logs
- `/xpadmin setchannel [channel]` - Set daily XP bonus channel
- `/welcome setchannel [channel]` - Set welcome message channel
- `/bday setposttime <time>` - Set birthday message post time
- `/settimezone <timezone>` - Set server timezone

### Owner Commands (Bot Owner Only)
- `/owner status` - Detailed bot and system status
- `/owner restart` - Restart the bot
- `/owner shutdown` - Shutdown the bot
- `/owner setonline` - Configure online message and channel

## Security Features

- Triple-layer Owner Verification: Direct ID check, helper function check, and detailed logging
- Permission-based Commands: Admin commands require appropriate server permissions
- Secure Configuration: Sensitive data stored in `.env` with proper file permissions
- Health Monitoring: Continuous system health checks with automated alerts
- Crash Detection: Automatic crash flag management with safe mode recovery
- Data Protection: Database backups with retention policies

## Troubleshooting

If you encounter any issues:

1. Check the logs in the `data/logs/` directory
2. Verify all environment variables are correctly set in `.env`
3. Ensure the bot has proper permissions in Discord
4. Make sure all intents are enabled in the Discord Developer Portal

For additional support, please refer to the individual cog files or contact the developer.
