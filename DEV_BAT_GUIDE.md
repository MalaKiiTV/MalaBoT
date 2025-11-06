# How to Use dev.bat for MalaBoT Development

## Overview
The `dev.bat` file is a comprehensive development tool that makes it easy to manage your MalaBoT locally. I've updated it to be more user-friendly and to help you pull updates from the main branch easily.

## Quick Start Guide

### 1. Pull Updates from GitHub
The most important feature for you is **Option 13** - this pulls all the latest updates from the main branch:

1. Run `dev.bat`
2. Choose option **13** from the menu
3. It will:
   - Switch to the main branch automatically
   - Stash any local changes you've made
   - Pull the latest updates
   - Offer to restore your local changes

### 2. Start the Bot
After pulling updates, use **Option 1** to start the bot:
1. Choose option **1**
2. It validates your configuration
3. Starts the bot in a new window

### 3. Check Bot Status
Use **Option 4** to see if the bot is running correctly:
- Shows running processes
- Displays database and log file status
- Shows recent log entries

## Menu Options Explained

### Bot Management
- **1. Start Bot** - Clears cache, validates config, starts bot in new window
- **2. Stop Bot** - Stops all running bot processes (multiple methods)
- **3. Restart Bot** - Stop, clear cache, restart bot
- **4. Check Bot Status** - View current status, logs, process information
- **5. View Live Logs** - Watch logs in real-time (press Ctrl+C to exit)
- **6. Clear All Caches** - Clear Python, pytest, and temp files

### Workflows
- **7. Update Workflow** - Pull + Install + Restart + Status (all in one)
- **8. Deploy Workflow** - Stage + Commit + Push to GitHub

### Git Operations
- **9. Check Git Status** - See what files have changed
- **10. Stage All Changes** - Prepare files for commit
- **11. Commit Changes** - Save changes with a message
- **12. Push to GitHub** - Upload your commits
- **13. Pull from GitHub** - ⭐ **MOST IMPORTANT FOR YOU** - Get latest updates
- **14. Switch Branch** - Change to different git branch
- **15. View Commit History** - See recent changes

### Utilities
- **16. Install Dependencies** - Update Python packages
- **17. Test Configuration** - Validate your .env file settings
- **18. Create Backup** - Backup database and logs
- **19. Environment Check** - Verify everything is set up correctly

## Your Typical Workflow

### After I Make Updates:
1. Run `dev.bat`
2. Choose option **13** (Pull from GitHub)
3. Confirm you want to continue (this will switch to main branch)
4. If you had local changes, choose whether to restore them
5. Once updated, choose option **1** (Start Bot)
6. Test the new features

### If You Make Local Changes:
1. Make your changes to files
2. Run `dev.bat`
3. Choose option **9** (Check Git Status) to see what changed
4. Choose option **10** (Stage All Changes)
5. Choose option **11** (Commit Changes) - enter a descriptive message
6. Choose option **12** (Push to GitHub) if you want to share your changes

## Troubleshooting

### If Pull Fails:
- Make sure you have internet connection
- If you have conflicting changes, the script will tell you
- Use option **9** (Check Git Status) to see issues

### If Bot Won't Start:
- Use option **17** (Test Configuration) to check .env file
- Use option **16** (Install Dependencies) to update packages
- Check the logs with option **5** (View Live Logs)

### If Git Operations Fail:
- Make sure you're in the correct directory
- Use option **19** (Environment Check) to verify git setup
- Check your GitHub permissions

## Key Improvements Made

1. **Simplified Menu** - Removed complex droplet operations, focused on local development
2. **Better Error Handling** - More helpful error messages and recovery options
3. **Automatic Branch Switching** - Option 13 automatically switches to main branch
4. **Stash/Restore** - Protects your local changes during updates
5. **Improved Git Configuration** - Better handling of authentication and merges

## Environment Setup

Make sure you have:
- Python 3.8+ installed
- Git installed and configured
- `.env` file with your Discord bot token
- Required dependencies (can be installed with option 16)

## Safety Features

- Automatic backup of local changes during pulls
- Configuration validation before starting bot
- Graceful error handling with helpful messages
- Clear status indicators throughout operations

---

**Tip**: Option 13 is your best friend for keeping your local copy up to date with my fixes and improvements!