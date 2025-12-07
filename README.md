# 🤖 MalaBoT

A powerful, multifunctional Discord bot built with discord.py featuring XP systems, moderation tools, Warzone verification, and more.

## ✨ Features

### 🎮 Core Systems
- **XP & Leveling System** - Track user activity with customizable XP rewards and level roles
- **Moderation Tools** - Comprehensive moderation commands (kick, ban, mute, delete messages)
- **Warzone Verification** - Activision ID verification system with screenshot review
- **Birthday Tracking** - Automatic birthday announcements and special roles
- **Welcome/Goodbye Messages** - Customizable member join/leave messages
- **Appeal System** - Allow banned users to submit appeals for review

### 🛠️ Utility Features
- **Server Statistics** - Detailed server and user information commands
- **Health Monitoring** - Built-in health checks and watchdog system
- **Automatic Backups** - Database backup system with verification
- **Role Connections** - Advanced role management and protection
- **Fun Commands** - Jokes, facts, 8ball, dice rolling, and more

### 🔧 Admin Features
- **Setup Wizard** - Easy configuration through Discord UI
- **Owner Commands** - Bot control, restart, and diagnostics
- **Audit Logging** - Comprehensive event logging and tracking
- **Safe Mode** - Automatic crash recovery system

## 📋 Requirements

- Python 3.11 or higher
- Discord Bot Token
- Required Python packages (see `requirements.txt`)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/MalaKiiTV/MalaBoT.git
cd MalaBoT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Required Settings
DISCORD_TOKEN=your_discord_bot_token_here
OWNER_IDS=123456789012345678,987654321098765432
BOT_PREFIX=/

# Optional Settings
BOT_NAME=MalaBoT
BOT_VERSION=1.0.0
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
LOG_FILE=data/logs/bot.log

# Feature Flags
ENABLE_MODERATION=true
ENABLE_FUN=true
ENABLE_UTILITY=true
ENABLE_HEALTH_MONITOR=true
ENABLE_WATCHDOG=true

# Owner Notifications
OWNER_ALERTS_ENABLED=true
OWNER_DAILY_DIGEST_ENABLED=true
OWNER_DAILY_DIGEST_TIME=00:00

# Debug (for development only)
DEBUG_GUILDS=
```

### 4. Run the Bot
```bash
python bot.py
```

## 📝 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token from the Developer Portal | `MTIzNDU2Nzg5MDEyMzQ1Njc4.GhIjKl.MnOpQrStUvWxYz` |
| `OWNER_IDS` | Comma-separated list of Discord user IDs with owner permissions | `123456789012345678,987654321098765432` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_PREFIX` | Command prefix for text commands | `/` |
| `BOT_NAME` | Display name for the bot | `MalaBoT` |
| `BOT_VERSION` | Version string | `1.0.0` |
| `DATABASE_URL` | SQLite database path | `sqlite:///data/bot.db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `LOG_FILE` | Path to log file | `data/logs/bot.log` |
| `DEBUG_GUILDS` | Comma-separated guild IDs for instant command sync (dev only) | `` |

### Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_MODERATION` | Enable moderation commands | `true` |
| `ENABLE_FUN` | Enable fun commands | `true` |
| `ENABLE_UTILITY` | Enable utility commands | `true` |
| `ENABLE_HEALTH_MONITOR` | Enable health monitoring | `true` |
| `ENABLE_WATCHDOG` | Enable watchdog system | `true` |

## 🎮 Commands

### User Commands
- `/help` - Display all available commands
- `/ping` - Check bot latency
- `/userinfo [@user]` - View user information
- `/serverinfo` - View server information
- `/xp rank` - Check your XP and level
- `/xp leaderboard` - View server XP leaderboard
- `/bday set <date>` - Set your birthday

### Moderation Commands (Requires Permissions)
- `/delete <amount>` - Delete messages
- `/kick <user> [reason]` - Kick a user
- `/ban <user> [reason]` - Ban a user
- `/mute <user> <duration> [reason]` - Temporarily mute a user
- `/unmute <user>` - Unmute a user

### Admin Commands
- `/setup` - Open the setup wizard
- `/verify review <user> <decision>` - Review verification submissions

### Owner Commands
- `/owner restart` - Restart the bot
- `/owner status` - View bot status
- `/clear-commands` - Clear and resync slash commands

## 🔧 Setup Guide

1. **Invite the Bot** to your server with appropriate permissions
2. **Run `/setup`** to open the configuration wizard
3. **Configure Features**:
   - Set up verification system (channel, roles)
   - Configure XP system (rewards, level roles)
   - Set birthday announcement channel
   - Configure welcome/goodbye messages
   - Set up moderation roles

## 📊 Database

MalaBoT uses SQLite for data storage. The database includes:
- User profiles (XP, levels, birthdays)
- Server settings and configurations
- Verification submissions
- Moderation logs and audit trails
- Appeal submissions
- Health check logs

### Automatic Backups
- Backups are created automatically
- Stored in `data/backups/`
- Configurable retention period
- Backup verification system

## 🛡️ Permissions

The bot requires the following Discord permissions:
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Manage Messages (for moderation)
- Manage Roles (for XP roles and verification)
- Kick Members (for moderation)
- Ban Members (for moderation)
- Manage Channels (for channel purge)

## 🔍 Troubleshooting

### Bot Not Responding
1. Check if the bot is online in your server
2. Verify the bot has proper permissions
3. Check the logs in `data/logs/bot.log`
4. Ensure slash commands are synced (use `/clear-commands` if needed)

### Commands Not Showing
1. Wait a few minutes for Discord to sync commands
2. Use `/clear-commands` to force resync
3. Check if `DEBUG_GUILDS` is set correctly (dev mode)

### Database Errors
1. Check if `data/` directory exists
2. Verify database file permissions
3. Check logs for specific error messages
4. Restore from backup if needed

## 📁 Project Structure

```
MalaBoT/
├── bot.py                 # Main bot file
├── config/
│   ├── settings.py       # Environment configuration
│   └── constants.py      # Static constants
├── cogs/                 # Feature modules
│   ├── moderation.py
│   ├── xp.py
│   ├── verify.py
│   ├── birthdays.py
│   ├── welcome.py
│   ├── fun.py
│   ├── utility.py
│   ├── owner.py
│   ├── setup.py
│   └── ...
├── database/
│   ├── models.py         # Database manager
│   └── migrations/       # Database migrations
├── utils/
│   ├── helpers.py        # Helper functions
│   ├── logger.py         # Logging setup
│   ├── backup_manager.py # Backup system
│   └── ...
├── data/
│   ├── bot.db           # SQLite database
│   ├── logs/            # Log files
│   └── backups/         # Database backups
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is private and proprietary. All rights reserved.

## 🆘 Support

For support, please contact the bot owner or create an issue in the repository.

## 🔄 Updates

To update the bot:
1. Pull the latest changes: `git pull`
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Restart the bot

## ⚙️ Development

### Debug Mode
Set `DEBUG_GUILDS` in `.env` to your test server ID for instant command sync:
```env
DEBUG_GUILDS=123456789012345678
```

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📊 Statistics

- **Total Lines of Code**: ~12,800
- **Cogs**: 13
- **Commands**: 50+
- **Database Tables**: 15+

## 🎯 Roadmap

- [ ] Music playback system
- [ ] Economy system with currency
- [ ] Custom command creation
- [ ] Reaction roles
- [ ] Ticket system
- [ ] Advanced analytics dashboard

---

**Made with ❤️ by MalaKiiTV**