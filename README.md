# 🤖 MalaBoT - Multifunctional Discord Bot

A feature-rich Discord bot built with discord.py, featuring XP systems, moderation tools, verification systems, and more!

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Discord.py Version](https://img.shields.io/badge/discord.py-2.x-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Development Tools](#-development-tools)
- [Commands](#-commands)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎮 Core Features
- **XP & Leveling System** - Track user activity and progression
- **Birthday Celebrations** - Automatic birthday announcements and roles
- **Verification System** - Warzone player verification with screenshot review
- **Welcome Messages** - Customizable welcome messages for new members
- **Moderation Tools** - Kick, ban, timeout, and warning systems
- **Fun Commands** - Jokes, facts, roasts, 8ball, dice rolling, and more

### 🛠️ Technical Features
- **Slash Commands** - Modern Discord slash command interface
- **Database Integration** - SQLite database for persistent data
- **Logging System** - Comprehensive logging and audit trails
- **Health Monitoring** - Automatic health checks and crash recovery
- **Scheduler** - Background tasks for birthdays and maintenance
- **Safe Mode** - Automatic recovery from crashes

### 🎯 Bot Commands
- `/help` - Show all available commands
- `/ping` - Check bot latency and uptime
- `/userinfo` - Display user information
- `/serverinfo` - Display server statistics
- `/verify` - Warzone verification system (parent command)
  - `/verify submit` - Submit verification screenshot
  - `/verify review` - Review submissions (staff only)
  - `/verify setup` - Setup verification channel (admin only)
- `/joke`, `/fact`, `/roast` - Fun entertainment commands
- `/8ball`, `/roll`, `/coinflip` - Random decision makers
- And many more!

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- Git (for version control)

### Installation

#### Windows (Recommended - Using dev.bat):
```bash
# 1. Clone the repository
git clone https://github.com/MalaKiiTV/MalaBoT.git
cd MalaBoT

# 2. Run dev.bat
dev.bat

# 3. Choose option 16 (Install Dependencies)
# 4. Choose option 17 (Create .env File)
# 5. Edit .env with your bot token
# 6. Choose option 1 (Start Bot)
```

#### Manual Installation:
```bash
# 1. Clone the repository
git clone https://github.com/MalaKiiTV/MalaBoT.git
cd MalaBoT

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Edit .env with your bot token
# Add your DISCORD_TOKEN and OWNER_IDS

# 5. Start the bot
python bot.py
```

---

## 🛠️ Development Tools

### dev.bat - All-in-One Development Tool

MalaBoT includes a comprehensive development tool (`dev.bat`) with 23+ options for managing your bot:

#### Quick Reference:
```
BOT MANAGEMENT:
  1. Start Bot              - Start with cache clear
  2. Stop Bot               - Stop running bot
  3. Restart Bot            - Restart with cache clear
  4. Check Bot Status       - View status and logs
  5. View Live Logs         - Real-time log monitoring
  6. Clear All Caches       - Clear Python/temp caches

WORKFLOWS:
  7. Update Workflow        - Pull → Restart → Status
  8. Deploy Workflow        - Stage → Commit → Push

GIT OPERATIONS:
  9.  Check Git Status      - View changes
  10. Stage All Changes     - Stage for commit
  11. Commit Changes        - Commit with message
  12. Push to GitHub        - Push commits
  13. Remote Deploy         - Deploy to production
  14. Pull from GitHub      - Get latest changes ⭐
  15. View Commit History   - Last 10 commits

UTILITIES:
  16. Install Dependencies  - Install/update packages
  17. Create .env File      - Create from template
  18. Test Configuration    - Validate settings

ADVANCED OPS:
  19. Full Clean Update     - Complete clean update
  20. Backup Now            - Backup logs and DB
  21. Verify Environment    - Check configuration
  22. Clear All             - Complete system cleanup ⭐
  23. Fix /verify Command   - Fix command structure ⭐

EXIT:
  0. Exit                   - Close dev.bat
```

**📖 For detailed explanations of each option, see [DEV_BAT_GUIDE.md](DEV_BAT_GUIDE.md)**

### Utility Scripts

#### cleanup.py
Complete system cleanup utility:
```bash
python cleanup.py
```
Clears: Python cache, pytest cache, temp files, old logs, Discord cache, build artifacts

#### clear_and_sync.py
Discord command sync utility:
```bash
python clear_and_sync.py
```
Clears all Discord slash commands and prepares for fresh sync

#### fix_verify_command.py
Fix /verify command structure:
```bash
python fix_verify_command.py
```
Fixes /verify to show as parent command with subcommands

---

## 📝 Commands

### Utility Commands
- `/help` - Show all available commands
- `/ping` - Check bot latency and uptime
- `/userinfo [user]` - Display user information
- `/serverinfo` - Display server statistics
- `/about` - Bot information and version
- `/serverstats` - Detailed server statistics

### Fun Commands
- `/joke` - Get a random joke
- `/fact` - Learn a random fact
- `/roast [target]` - Roast someone (or the bot!)
- `/8ball <question>` - Ask the magic 8-ball
- `/roll [sides] [count]` - Roll dice
- `/coinflip` - Flip a coin

### Verification System
- `/verify submit <activision_id> <platform>` - Submit verification (attach screenshot)
- `/verify review <user> <decision> [notes]` - Review submission (staff only)
- `/verify setup <channel>` - Setup review channel (admin only)

### Owner Commands
- `/owner status` - Bot status report
- `/owner restart` - Restart the bot
- `/owner shutdown` - Shutdown the bot
- `/owner clearcrash` - Clear crash flags
- `/owner setonline` - Set online message

---

## ⚙️ Configuration

### .env File
Create a `.env` file in the root directory with the following:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=/
BOT_NAME=MalaBoT
BOT_VERSION=1.0.0
OWNER_IDS=your_discord_user_id_here

# Bot Settings
LOG_LEVEL=INFO
LOG_FILE=data/logs/bot.log

# Feature Flags
ENABLE_MODERATION=true
ENABLE_FUN=true
ENABLE_UTILITY=true

# Optional: Debug Guilds (for instant command sync)
DEBUG_GUILDS=your_server_id_here
```

### Getting Your Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section
4. Click "Reset Token" and copy it
5. Paste it in your `.env` file as `DISCORD_TOKEN`

### Getting Your User ID
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click your username
3. Click "Copy ID"
4. Paste it in your `.env` file as `OWNER_IDS`

---

## 🚀 Deployment

### Local Development
```bash
# Use dev.bat for easy management
dev.bat

# Or run directly
python bot.py
```

### Production Deployment (DigitalOcean Droplet)
```bash
# Using dev.bat (Recommended)
dev.bat → Option 13 (Remote Deploy to Droplet)

# Manual deployment
ssh malabot@165.232.156.230
cd /home/malabot/MalaBoT
git pull origin main
pkill -f bot.py
nohup python3 bot.py > data/logs/latest.log 2>&1 &
```

### Docker Deployment (Coming Soon)
```bash
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Commands Not Showing in Discord

**Solution 1: Use Clear All (Recommended)**
```bash
dev.bat → Option 22 (Clear All)
dev.bat → Option 1 (Start Bot)
Wait 30 seconds, test in Discord
```

**Solution 2: Fix /verify Command**
```bash
dev.bat → Option 23 (Fix /verify Command)
dev.bat → Option 1 (Start Bot)
Wait 30 seconds, test in Discord
```

**Solution 3: Manual Fix**
```bash
python clear_and_sync.py
python bot.py
```

### Bot Won't Start

**Check Configuration:**
```bash
dev.bat → Option 18 (Test Configuration)
```

**Check Logs:**
```bash
dev.bat → Option 5 (View Live Logs)
```

**Common Issues:**
- Missing or invalid `DISCORD_TOKEN` in `.env`
- Missing `OWNER_IDS` in `.env`
- Missing dependencies (run option 16)

### Git Push Fails

**Solution:**
```bash
dev.bat → Option 14 (Pull from GitHub)
dev.bat → Option 12 (Push to GitHub)
```

**If still failing:**
```bash
# Set GITHUB_TOKEN environment variable
set GITHUB_TOKEN=your_github_token_here
dev.bat → Option 12 (Push to GitHub)
```

### Bot Running But Not Responding

**Check Status:**
```bash
dev.bat → Option 4 (Check Bot Status)
```

**Restart Bot:**
```bash
dev.bat → Option 3 (Restart Bot)
```

**Clear Caches:**
```bash
dev.bat → Option 6 (Clear All Caches)
dev.bat → Option 3 (Restart Bot)
```

---

## 📚 Documentation

- **[DEV_BAT_GUIDE.md](DEV_BAT_GUIDE.md)** - Complete dev.bat reference with all 23 options explained
- **[FILES_TO_DELETE.md](FILES_TO_DELETE.md)** - Guide for cleaning up unnecessary files
- **[COMMAND_FIX.md](COMMAND_FIX.md)** - Troubleshooting guide for command sync issues

---

## 🔄 Updating MalaBoT

### Getting Latest Updates

**Using dev.bat (Recommended):**
```bash
dev.bat → Option 14 (Pull from GitHub)
dev.bat → Option 3 (Restart Bot)
```

**Using Update Workflow:**
```bash
dev.bat → Option 7 (Update Workflow)
# This does: Pull → Install Dependencies → Restart → Check Status → Show Logs
```

**Manual Update:**
```bash
git pull origin main
pip install -r requirements.txt
python bot.py
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the Discord bot community
- Special thanks to all contributors

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/MalaKiiTV/MalaBoT/issues)
- **Discord:** [Join our server](https://discord.gg/your-invite-link)
- **Documentation:** [Wiki](https://github.com/MalaKiiTV/MalaBoT/wiki)

---

## 🎯 Roadmap

- [ ] Music commands
- [ ] Economy system
- [ ] Custom commands
- [ ] Web dashboard
- [ ] Docker support
- [ ] Multi-language support
- [ ] Advanced analytics

---

**Made with ❤️ by MalaKii**

**Last Updated:** 2025-10-28
**Version:** 1.0.0