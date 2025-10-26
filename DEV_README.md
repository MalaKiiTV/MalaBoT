# MalaBoT Development Guide

## 🚀 Quick Start

### Using the Development Script

The `dev.bat` file is your main tool for managing MalaBoT locally. Simply double-click it or run from command line:

```bash
dev.bat
```

## 📋 Available Options

### 🔧 Bot Management
- **1. Start Bot**: Starts the Discord bot with cache clearing
- **2. Stop Bot**: Safely stops all bot processes  
- **3. Restart Bot**: Stops and restarts the bot
- **4. Check Bot Status**: Shows if the bot is running
- **5. Clear All Caches**: Cleans Python cache and temporary files

### 🔄 Git Operations
- **6. Check Git Status**: Shows current git status
- **7. Stage All Changes**: Stages all modified files
- **8. Commit Changes**: Commits staged changes with a message
- **9. Push to GitHub**: Pushes commits to the main branch
- **10. Pull from GitHub**: Pulls latest changes from GitHub
- **11. View Commit History**: Shows last 10 commits

### 🎯 Complete Workflows
- **12. Update Workflow**: Pull latest changes → Restart bot → Check status
- **13. Deploy Workflow**: Stage → Commit → Push changes to GitHub

### 🛠️ Utilities
- **14. Install/Update Dependencies**: Installs requirements.txt packages
- **15. Create .env file**: Creates .env from template

## 🔑 Setup Requirements

### 1. Python Installation
Make sure Python 3.8+ is installed and in your PATH.

### 2. Bot Configuration
The script will automatically create a `.env` file if it doesn't exist:

1. Copy `.env.example` to `.env` (done automatically)
2. Edit `.env` file with your bot token:
   ```
   DISCORD_BOT_TOKEN=your_actual_bot_token_here
   ```

### 3. Dependencies
The script automatically installs dependencies from `requirements.txt`.

## 📝 Common Workflows

### Daily Development
1. Run `dev.bat`
2. Choose option 1 to start the bot
3. Make your changes
4. Use options 7-9 to commit and push changes

### Updating Your Bot
1. Use option 12 (Update Workflow)
2. This pulls latest changes and restarts the bot automatically

### Deploying Changes
1. Use option 13 (Deploy Workflow)
2. Follow prompts to stage, commit, and push changes

## 🐛 Troubleshooting

### Bot Won't Start
- Check if `.env` file exists and contains your bot token
- Ensure Python and dependencies are installed (option 14)
- Check if the token is valid and bot has proper permissions

### Git Issues
- Make sure you're authenticated with GitHub
- Check if you have push permissions to the repository
- Use option 6 to check git status for any issues

### Process Issues
- Use option 2 to forcefully stop all bot processes
- Use option 5 to clear caches if experiencing weird behavior

## 📁 File Structure

```
MalaBoT/
├── bot.py              # Main bot file
├── dev.bat             # Main development script
├── dev_simple.bat      # Simplified version (core functions only)
├── dev_original_backup.bat  # Backup of original dev.bat
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .env               # Your actual environment variables (create this)
├── cogs/              # Bot commands/modules
├── config/            # Configuration files
├── database/          # Database models and files
└── utils/             # Utility functions
```

## 🔄 Alternative Scripts

### dev_simple.bat
If you prefer a simpler interface with just the core functions:
- Start, Stop, Restart bot
- Update (pull + restart)
- Push changes
- Quick deploy

Run it the same way: `dev_simple.bat`

## 💡 Pro Tips

1. **Always commit before updating** to avoid losing local changes
2. **Check bot status** after restarting to ensure it's running properly
3. **Use the update workflow** (option 12) for safe updates
4. **Keep your .env file secure** - never commit it to git!
5. **Clear caches** if you experience strange behavior after updates

## 🆘 Getting Help

If you encounter issues:
1. Check this README first
2. Use the bot status option to see what's running
3. Clear caches and try restarting
4. Check that your .env file is properly configured

Happy coding with MalaBoT! 🤖