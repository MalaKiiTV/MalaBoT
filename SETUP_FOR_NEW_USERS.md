# Setup Guide for New Users

## Overview

This bot is **fully portable** and can run on any Discord server! Each server has independent configuration with no conflicts.

## Quick Start (5 Minutes)

### Step 1: Get Your Bot Token

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "MyBot")
4. Go to "Bot" section
5. Click "Reset Token" and copy it
6. **Keep this secret!** Anyone with this token can control your bot

### Step 2: Get Your User ID

1. Open Discord
2. Go to Settings → Advanced
3. Enable "Developer Mode"
4. Right-click your username
5. Click "Copy ID"
6. Save this number

### Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your values:
   ```env
   DISCORD_TOKEN=your_bot_token_from_step_1
   OWNER_IDS=your_user_id_from_step_2
   ```

3. Save the file

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Bot

```bash
python bot.py
```

You should see:
```
🚀 MALABOT STARTUP SEQUENCE
✅ Logging system ready
✅ Startup backup created
✅ All critical checks passed
✅ STARTUP COMPLETE
```

### Step 6: Invite Bot to Your Server

1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to "OAuth2" → "URL Generator"
4. Select scopes:
   - `bot`
   - `applications.commands`
5. Select bot permissions:
   - Administrator (or specific permissions you need)
6. Copy the generated URL
7. Open it in browser and invite to your server

### Step 7: Configure Your Server

1. In Discord, run `/setup`
2. You'll see a menu with options:
   - ✅ Verification
   - 👋 Welcome
   - 🎂 Birthday
   - 🏆 XP
   - ⚙️ General
   - 🔗 Role Connections
3. Click each option to configure
4. All settings are saved automatically

**Done!** Your bot is now running and configured for your server.

## Features You Can Configure

### 1. Verification System
- Review channel for verification submissions
- Verified role to assign
- Cheater role and jail channel
- Platform selection (Xbox, PlayStation, PC, Mobile)

**User Command:** `/verify submit`

### 2. Welcome/Goodbye Messages
- Welcome channel and message
- Goodbye channel and message
- Custom titles and images
- Variables: `{member}`, `{member.name}`, `{server}`, `{member.count}`

**Automatic:** Triggers when members join/leave

### 3. Birthday System
- Birthday announcement channel
- Custom birthday message
- Announcement time (timezone-aware)

**User Commands:** `/birthday set`, `/birthday remove`

### 4. XP System
- Level-up announcement channel
- XP per message, reaction, voice minute
- XP cooldown
- Level role rewards

**User Commands:** `/xp rank`, `/xp leaderboard`, `/xp daily`

### 5. Role Connections
- Automatic role assignment based on conditions
- AND/OR logic
- Protected roles (exempt from rules)

**Example:** Give "Verified" role when user has "Member" role

### 6. General Settings
- Server timezone
- Online message and channel
- Moderator role
- Auto-assign role on join

## Multi-Server Support

### Your Bot Can Be In Multiple Servers!

Each server has **completely independent** configuration:

**Server A:**
- Verification enabled
- Welcome messages enabled
- XP system enabled

**Server B:**
- Only birthday system enabled
- Different timezone
- Different settings

**Server C:**
- Nothing configured yet
- Bot still works fine

**No conflicts!** Each server owner configures their own server via `/setup`.

## Permission Levels

### Server Owner (Guild Owner)
- Can run `/setup` to configure their server
- Can configure all features for their server
- Cannot affect other servers
- Cannot access bot owner commands

### Bot Owner (You)
- Can run owner commands (`/sync`, `/reload`, `/shutdown`, etc.)
- Can access all servers' data
- Cannot run `/setup` on servers you don't own (unless you're also the server owner)

### Moderators
- Can review verifications (if mod role set)
- Can review appeals (if mod role set)
- Configured per-server via `/setup` → General Settings

## Owner Commands (Bot Owner Only)

These commands are **only for you** (the person running the bot):

- `/sync` - Sync slash commands to Discord
- `/reload <cog>` - Reload a cog without restarting
- `/load <cog>` - Load a cog
- `/unload <cog>` - Unload a cog
- `/shutdown` - Shutdown the bot
- `/eval <code>` - Evaluate Python code
- `/sql <query>` - Execute SQL query
- `/logs` - View recent logs
- `/status` - View bot status
- `/guilds` - List all servers bot is in

**Note:** Regular users cannot access these commands.

## File Structure

```
MalaBoT/
├── .env                    # Your configuration (create from .env.example)
├── .env.example           # Template configuration file
├── bot.py                 # Main bot file
├── requirements.txt       # Python dependencies
├── config/               # Bot configuration
│   ├── settings.py       # Settings loader
│   └── constants.py      # Constants
├── cogs/                 # Bot features (cogs)
│   ├── setup.py          # /setup command
│   ├── verify.py         # Verification system
│   ├── welcome.py        # Welcome/goodbye
│   ├── birthdays.py      # Birthday system
│   ├── xp.py            # XP system
│   ├── role_connections.py  # Role connections
│   └── ...
├── database/            # Database
│   ├── models.py        # Database schema
│   └── migrations/      # Database migrations
├── utils/               # Utilities
│   ├── backup_manager.py    # Automatic backups
│   ├── safe_database.py     # Safe database operations
│   ├── health_checker.py    # Health monitoring
│   ├── enhanced_logger.py   # Logging system
│   └── startup_manager.py   # Startup verification
└── data/                # Data directory (created on first run)
    ├── bot.db           # SQLite database
    ├── backups/         # Automatic backups
    └── logs/            # Log files
```

## Troubleshooting

### Bot Won't Start

**Check:**
1. Is `DISCORD_TOKEN` correct in `.env`?
2. Did you install dependencies? (`pip install -r requirements.txt`)
3. Check `data/logs/bot.log` for errors

### Commands Not Showing

**Solution:**
1. Run `/sync` (bot owner only)
2. Wait 5 minutes
3. Restart Discord client
4. Commands should appear

### `/setup` Says "Permission Denied"

**Reason:** Only the **server owner** can run `/setup`

**Solution:** 
- If you own the server: Make sure you're the owner in Server Settings
- If you don't own the server: Ask the server owner to run `/setup`

### Features Not Working

**Check:**
1. Run `/setup` → "View Current Config"
2. Verify settings are configured
3. Check `data/logs/` for errors
4. Run `/healthcheck` (bot owner only)

### Database Errors

**Solution:**
1. Check `data/logs/database.log`
2. Verify `data/bot.db` exists
3. Check file permissions
4. Restore from backup if needed (see `data/backups/`)

## Advanced Configuration

### Using PostgreSQL Instead of SQLite

1. Install PostgreSQL
2. Create database
3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

### Running on Linux Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run in background with nohup
nohup python bot.py > data/logs/latest.log 2>&1 &

# Or use systemd service (recommended)
# Create /etc/systemd/system/malabot.service
```

### Running with Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## Security Best Practices

1. **Never share your bot token** - Anyone with it can control your bot
2. **Keep `.env` file secret** - It's in `.gitignore` for a reason
3. **Use environment variables** - Don't hardcode sensitive data
4. **Regular backups** - Bot creates daily backups automatically
5. **Monitor logs** - Check `data/logs/` regularly
6. **Update dependencies** - Run `pip install -r requirements.txt --upgrade` periodically

## Getting Help

### Check Documentation
- `QUICK_START.md` - Quick setup guide
- `PRODUCTION_READY_SUMMARY.md` - System overview
- `INTEGRATION_GUIDE.md` - Advanced integration
- `PORTABILITY_AUDIT.md` - Multi-server details

### Check Logs
- `data/logs/bot.log` - Main bot events
- `data/logs/errors.log` - All errors
- `data/logs/database.log` - Database operations
- `data/logs/{feature}.log` - Feature-specific logs

### Common Issues
- Commands not showing → Run `/sync` and wait
- Permission denied → Must be server owner for `/setup`
- Database errors → Check logs and restore from backup
- Bot offline → Check token and internet connection

## Contributing

If you want to add features or fix bugs:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Credits

Created by MalaKiiTV
Built with discord.py

---

**You're all set!** Your bot is now running and ready to use. Each server owner can configure their own settings via `/setup` without any conflicts.