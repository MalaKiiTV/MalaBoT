# MalaBoT Deployment Guide

## Critical Issues to Fix Immediately

### 1. Environment Configuration
Your `.env` file is missing critical information:

```env
# REQUIRED - Add your actual Discord bot token here
DISCORD_TOKEN=your_actual_bot_token_here

# REQUIRED - Add your Discord user ID here (and any other owner IDs)
OWNER_IDS=your_discord_user_id_here

# The rest can stay as is or be customized as needed
BOT_PREFIX=/
BOT_NAME=MalaBoT
BOT_VERSION=1.0.0
DEBUG_GUILDS=
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
LOG_FILE=data/logs/bot.log
ENABLE_STARTUP_VERIFICATION=true
ENABLE_AUTO_REPAIR=true
ENABLE_MUSIC=false
ENABLE_MODERATION=true
ENABLE_FUN=true
ENABLE_UTILITY=true
ENABLE_SAFE_MODE=true
OWNER_ALERTS_ENABLED=true
OWNER_DAILY_DIGEST_ENABLED=true
OWNER_DAILY_DIGEST_TIME=00:00
OWNER_STATUS_CHANNEL_ID=
ENABLE_HEALTH_MONITOR=true
ENABLE_WATCHDOG=true
WATCHDOG_INTERVAL=60
WATCHDOG_RESTART_DELAY=5
WEATHER_API_KEY=
YOUTUBE_API_KEY=
REDDIT_API_KEY=
```

### 2. GitHub Repository Setup
To properly use Git with your bot:

1. Create a new repository on GitHub for your bot
2. Initialize your local directory as a Git repository (already done):
   ```bash
   git init
   git checkout -b main
   ```
3. Add and commit your files:
   ```bash
   git add .
   git config --global user.email "your_email@example.com"
   git config --global user.name "Your Name"
   git commit -m "Initial commit with MalaBoT files"
   ```
4. Connect to your remote GitHub repository:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

### 3. File Updates Required
Replace these files in your bot directory with the fixed versions:

- `cogs/welcome.py` - Fixed command registration
- `cogs/moderation.py` - Added kick, ban, mute, unmute commands with proper permissions
- `cogs/xp.py` - Fixed setup function to properly register commands
- `cogs/utility.py` - Added /about and /serverstats commands (if missing)

## How to Deploy the Fixed Version

### Option 1: Manual File Replacement
1. Extract the `fixes` directory from `MalaBoT-COMPLETE-FIXED.zip`
2. Replace your existing files with the fixed versions:
   ```bash
   cp fixes/cogs/welcome.py cogs/welcome.py
   cp fixes/cogs/moderation.py cogs/moderation.py
   cp fixes/cogs/xp.py cogs/xp.py
   cp fixes/cogs/utility.py cogs/utility.py
   ```
3. Update your `.env` file with your actual bot token and owner ID
4. Run the update script:
   - Windows: `update.bat`
   - Linux: `./update_droplet.sh`

### Option 2: Git-Based Deployment
1. After pushing your fixed code to GitHub, on your droplet:
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   ```
2. Update your `.env` file with your actual bot token and owner ID
3. Restart your bot

## Command Permissions Explained

### Owner-Only Commands
- `/owner status` - Check bot system status
- `/owner restart` - Restart the bot
- `/owner shutdown` - Shutdown the bot
- `/owner setonline` - Set online notification channel and message

These commands can ONLY be used by users whose IDs are listed in the `OWNER_IDS` setting in your `.env` file.

### Admin-Only Commands
- `/delete` - Message deletion commands
- `/xpadmin` - XP system administration
- `/welcome` - Welcome system configuration
- `/kick` - Kick users from server
- `/ban` - Ban users from server
- `/mute` - Mute users in server
- `/unmute` - Unmute users in server

These commands can ONLY be used by:
1. Bot owners (listed in `OWNER_IDS`)
2. Users with Administrator permission in Discord
3. Users with specific permissions (Kick Members, Ban Members, Moderate Members)

### Public Commands
All other commands are available to everyone:
- `/help` - Command help
- `/ping` - Bot latency check
- `/userinfo` - User information
- `/serverinfo` - Server information
- `/about` - Bot information
- `/serverstats` - Server statistics
- `/joke` - Random joke
- `/fact` - Random fact
- `/roast` - Roast a user
- `/8ball` - Magic 8-ball
- `/roll` - Dice roll
- `/coinflip` - Coin flip
- `/xp` - XP rank and leaderboard
- `/bday` - Birthday commands

## Troubleshooting Common Issues

### Bot Not Starting
1. Check that `DISCORD_TOKEN` is set in `.env`
2. Check logs in `data/logs/latest.log`
3. Ensure all required intents are enabled in Discord Developer Portal:
   - Server Members Intent
   - Message Content Intent

### Commands Not Appearing
1. Wait up to 1 hour for global command sync (or use debug guilds)
2. Check that all cogs loaded successfully in logs
3. Verify the bot has Administrator permissions in Discord

### Permission Issues
1. Ensure your user ID is in `OWNER_IDS` for owner commands
2. Verify you have appropriate Discord permissions for admin commands
3. Check logs for permission denied messages

## GitHub Integration Benefits

### Automated Deployments
1. Set up a webhook on your GitHub repository to automatically deploy when you push changes
2. Use GitHub Actions to automatically test and deploy your bot

### Version Control
1. Track changes to your bot
2. Rollback to previous versions if needed
3. Collaborate with others on bot development

### Backup and Recovery
1. Keep your code safe in the cloud
2. Easily restore your bot if something goes wrong

To set up GitHub integration properly:
1. Push your code to GitHub regularly
2. Use `git pull` on your droplet to update
3. Consider setting up SSH keys for passwordless authentication