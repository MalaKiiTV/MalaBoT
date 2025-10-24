# MalaBoT - Multifunctional Discord Bot

![MalaBoT Logo](https://i.imgur.com/example.png)

MalaBoT is a powerful, multifunctional Discord bot built with discord.py, designed to enhance server engagement with comprehensive XP systems, moderation tools, entertainment features, and much more.

## 🚀 Features

### 🏆 XP & Leveling System
- **Automatic XP Gain**: Users earn XP for messaging with configurable cooldowns
- **Daily Check-ins**: Bonus XP for first message of the day with streak bonuses
- **Level Progression**: Comprehensive leveling system with role rewards
- **Leaderboards**: Server-wide XP rankings and statistics
- **Admin Controls**: Full XP administration commands

### 🔥 Roast XP System
- **Bot Progression**: Unique XP system where the bot gains XP when roasted
- **Title System**: Bot unlocks new roast titles as it levels up
- **Roast Leaderboard**: Track users who've roasted the bot most
- **Custom Titles**: Server owners can set custom final roast titles

### 🎂 Birthday System
- **Birthday Tracking**: Users can set their birthdays
- **Automatic Celebrations**: Bot posts birthday messages and assigns temporary roles
- **Timezone Support**: Configurable server timezones
- **Birthday Lists**: View upcoming birthdays and server-wide birthday calendar

### 👋 Welcome System
- **Custom Embeds**: Personalized welcome messages with images
- **Role Assignment**: Automatic role management for new members
- **Birthday Catch-up**: Immediate birthday recognition for new members
- **Customizable Content**: Full control over welcome messages and styling

### 🛡️ Moderation System
- **Message Deletion**: Bulk message cleanup with logging
- **Audit Logging**: Comprehensive moderation action tracking
- **Permission Levels**: Granular permission system for different roles
- **Safe Mode**: Automatic protection during system issues

### 🎮 Fun Commands
- **Jokes & Facts**: Random entertainment content
- **Roast Battles**: Interactive roasting system
- **8-Ball**: Magic 8-ball fortune telling
- **Dice Rolling**: Customizable dice with statistics
- **Coin Flips**: Classic 50/50 coin flips

### ⚙️ Utility Commands
- **Help System**: Comprehensive command documentation
- **User Information**: Detailed user statistics and profiles
- **Server Stats**: Comprehensive server analytics
- **Bot Status**: Real-time system health monitoring
- **Ping & Uptime**: Bot performance metrics

### 🔧 Advanced Features
- **Crash Recovery**: Automatic restart and recovery system
- **Health Monitoring**: Real-time system resource tracking
- **Update Automation**: One-click updates with backup protection
- **Audit Logging**: Complete event tracking and analysis
- **Daily Digest**: Automated owner reports and statistics
- **Safe Mode**: Limited functionality during system issues

## 📋 Requirements

- Python 3.8 or higher
- Discord bot token
- DigitalOcean droplet (recommended for production)
- Git for version control

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/MalaBoT.git
cd MalaBoT
```

2. **Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your bot token and settings
```

5. **Run the bot:**
```bash
python bot.py
```

### Production Deployment (DigitalOcean)

1. **Create droplet with Ubuntu 20.04+**
2. **Clone repository:**
```bash
cd /home/malabot
git clone https://github.com/your-username/MalaBoT.git
cd MalaBoT
```

3. **Set up environment:**
```bash
cp .env.example .env
# Configure with your production settings
chmod 600 .env
```

4. **Install dependencies and run:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x update.sh
./update.sh
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Discord Configuration
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=/
BOT_NAME=MalaBoT
BOT_VERSION=1.0.0
OWNER_IDS=your_owner_id_here
DEBUG_GUILDS=your_testing_server_ids

# Database
DATABASE_URL=sqlite:///data/bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/bot.log

# Feature Flags
ENABLE_MUSIC=false
ENABLE_MODERATION=true
ENABLE_FUN=true
ENABLE_UTILITY=true
ENABLE_SAFE_MODE=true

# Monitoring
ENABLE_HEALTH_MONITOR=true
ENABLE_WATCHDOG=true
OWNER_ALERTS_ENABLED=true
OWNER_DAILY_DIGEST_ENABLED=true

# API Keys (Optional)
WEATHER_API_KEY=
YOUTUBE_API_KEY=
REDDIT_API_KEY=
```

### Customization

#### XP System Configuration (`config/constants.py`)
```python
# XP Settings
XP_PER_MESSAGE_MIN = 5
XP_PER_MESSAGE_MAX = 15
XP_COOLDOWN_SECONDS = 60
DAILY_CHECKIN_XP = 50
STREAK_BONUS_PERCENT = 10

# Level Role Mapping
LEVEL_ROLE_MAP = {
    1: None,
    5: "Level 5",
    10: "Level 10",
    15: "Level 15",
    # ... add more levels as needed
}
```

#### Roast Titles
```python
ROAST_TITLES = {
    1: "Newbie Roaster",
    2: "Sassy Bot",
    # ... customize titles
    10: "Roast God",
}
```

## 📁 Project Structure

```
MalaBoT/
├── bot.py                 # Main bot entry point
├── .env                   # Environment configuration
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── update.sh             # Linux update script
├── update.bat            # Windows update script
├── README.md             # This file
│
├── cogs/                 # Bot command modules
│   ├── utility.py        # Utility commands
│   ├── fun.py           # Fun commands
│   ├── xp.py            # XP system
│   ├── owner.py         # Owner commands
│   └── ...              # Other cogs
│
├── config/              # Configuration files
│   ├── settings.py      # Environment loader
│   └── constants.py     # Bot constants
│
├── database/            # Database models
│   └── models.py        # Database schema
│
├── utils/               # Utility functions
│   ├── logger.py        # Logging system
│   └── helpers.py       # Helper functions
│
└── data/                # Runtime data
    ├── bot.db           # SQLite database
    ├── logs/            # Log files
    └── flags/           # System flags
```

## 🔄 Update Process

### Manual Updates

1. **Commit changes to Git:**
```bash
git add .
git commit -m "Update description"
git push origin main
```

2. **Update on server:**
```bash
# For production
./update.sh

# For development
./update.sh manual
```

### Automatic Updates

The update script handles:
- Graceful bot shutdown
- Git repository synchronization
- Dependency updates
- Database migrations
- Log backups
- Automatic restart

## 📊 Commands

### Utility Commands
- `/help` - Show all commands
- `/ping` - Bot latency and uptime
- `/userinfo [@user]` - User information
- `/serverinfo` - Server details
- `/about` - Bot information
- `/serverstats` - Server statistics

### XP Commands
- `/xp rank` - Your XP rank
- `/xp leaderboard` - Server leaderboard
- `/xpadmin setchannel` - Set daily XP channel

### Fun Commands
- `/joke` - Random joke
- `/fact` - Random fact
- `/roast [@user]` - Roast someone
- `/8ball [question]` - Magic 8-ball
- `/roll [sides] [count]` - Roll dice
- `/coinflip` - Flip a coin

### Owner Commands
- `/owner status` - Bot status
- `/owner restart` - Restart bot
- `/owner shutdown` - Shutdown bot
- `/owner clearcrash` - Clear crash flags

## 🔧 Maintenance

### Log Management
- Logs automatically rotate weekly
- Old logs are compressed and archived
- 30-day retention policy
- Manual log review in `data/logs/`

### Database Maintenance
- Automatic daily backups
- Integrity checks on startup
- Migration support for schema changes
- 30-day backup retention

### Health Monitoring
- Real-time resource monitoring
- Automatic crash detection
- Watchdog process for unresponsive states
- Owner notifications for critical issues

## 🛡️ Security

### File Permissions
```bash
chmod 600 .env              # Environment file
chmod 600 data/bot.db        # Database file
chmod 700 data/              # Data directory
```

### Security Practices
- Never commit `.env` or `bot.db` to version control
- Use SSH key authentication for server access
- Run bot under non-root user
- Regular token rotation
- Firewall configuration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include logging for all major operations
- Test thoroughly before deployment
- Document new features

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

**Bot won't start:**
- Check `.env` configuration
- Verify Discord token
- Check log files in `data/logs/`

**Commands not working:**
- Verify bot permissions
- Check slash command synchronization
- Review error logs

**High memory usage:**
- Check log file sizes
- Review database size
- Monitor system resources

### Getting Help

- 📧 Email: support@malabot.dev
- 💬 Discord: [Support Server](https://discord.gg/malabot)
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/MalaBoT/issues)
- 📖 Wiki: [Documentation](https://github.com/your-username/MalaBoT/wiki)

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [aiosqlite](https://github.com/amesghar/aiosqlite) - Async SQLite support
- [APScheduler](https://github.com/agronholm/apscheduler) - Task scheduling
- All contributors and users who make MalaBoT better!

---

**MalaBoT** - *Empowering Discord communities since 2024* 🚀