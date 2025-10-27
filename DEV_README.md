# MalaBoT Development Guide - COMPLETELY FIXED

## 🚨 **IMPORTANT READ FIRST**

Your original dev.bat had critical issues that prevented your bot from starting. I've completely rewritten it with proper error handling, logging, and diagnostics.

## 🔧 **What Was Fixed:**

- ❌ **Missing .env file handling** - Now auto-creates and validates
- ❌ **Missing data/logs directories** - Now auto-creates required directories  
- ❌ **No error visibility** - Added live log viewing and status checking
- ❌ **Process management issues** - Fixed window titles and process detection
- ❌ **No configuration testing** - Added validation before starting bot

## 🚀 **Quick Start**

### **Step 1: Run Diagnostic Tool**
```bash
diagnose.bat
```
This will:
- Check Python installation
- Install missing dependencies
- Create required directories
- Set up .env file from template
- Test configuration
- Verify bot can start

### **Step 2: Configure Your Bot**
Edit the `.env` file that was created:
```
DISCORD_TOKEN=your_actual_discord_bot_token
OWNER_IDS=your_discord_user_id_here
BOT_PREFIX=/
```

### **Step 3: Run Development Script**
```bash
dev.bat
```

## 📋 **Complete Menu Options Explained**

### 🔧 **Bot Management**
- **1. Start Bot** - Starts bot with cache clearing, validates config first
- **2. Stop Bot** - Safely stops all bot processes
- **3. Restart Bot** - Complete restart with validation and cache clearing
- **4. Check Bot Status** - Shows if bot is running + recent log entries
- **5. View Live Logs** - Real-time log viewing (press Ctrl+C to stop)
- **6. Clear All Caches** - Cleans Python cache, temp files, old logs

### 🔄 **Git Operations**
- **7. Check Git Status** - Shows current git status
- **8. Stage All Changes** - Stages all modified files
- **9. Commit Changes** - Commits with custom message
- **10. Push to GitHub** - Pushes commits to main branch
- **11. Pull from GitHub** - Pulls latest changes
- **12. View Commit History** - Shows last 10 commits

### 🎯 **Complete Workflows**
- **13. Update Workflow** - ⭐ **PULL → UPDATE DEPS → RESTART → SHOW STATUS**
- **14. Deploy Workflow** - Stage → Commit → Push with confirmation

### 🛠️ **Utilities**
- **15. Install/Update Dependencies** - Installs requirements.txt packages
- **16. Create .env file** - Creates .env from template with validation
- **17. Test Bot Configuration** - Tests all settings without starting bot

## 📝 **Option 13: Update Workflow - EXPLAINED**

**This is what option 13 does step-by-step:**

1. **Pull latest changes** from GitHub
2. **Install/update dependencies** from requirements.txt
3. **Restart the bot** (stop → clear cache → start)
4. **Check status** to confirm bot is running
5. **Show recent logs** to verify everything is working

## 📁 **update.bat Explanation**

Your `update.bat` script does the following:

### **What it does:**
1. **Stops running bot processes**
2. **Creates backups** of logs and important files
3. **Pulls updates** from Git if it's a repository
4. **Creates/activates virtual environment**
5. **Updates pip** and installs dependencies
6. **Cleans old backups** and cache
7. **Starts the bot** in minimized window
8. **Verifies bot is running**

### **When to use update.bat:**
- When you want to update AND run the bot automatically
- When you need a more robust update process with backups
- When working in production environment

### **When to use dev.bat option 13:**
- During development and testing
- When you want to see status and logs after update
- For quick update+restart cycles

## 🐛 **Troubleshooting Guide**

### **Bot Won't Start:**
1. Run `diagnose.bat` first
2. Check if `.env` file has correct `DISCORD_TOKEN`
3. Use option 17 to test configuration
4. Use option 5 to view error logs

### **Git Issues:**
1. Use option 6 to check git status
2. Make sure you're authenticated with GitHub
3. Check if you have push permissions

### **Process Issues:**
1. Use option 2 to forcefully stop all bot processes
2. Use option 6 to clear caches if experiencing weird behavior
3. Use option 4 to check exact status and recent errors

## 🎯 **Recommended Daily Workflow**

### **For Development:**
1. `dev.bat` → Option 13 (Update Workflow)
2. Make your changes
3. `dev.bat` → Option 14 (Deploy Workflow)

### **For Quick Testing:**
1. `dev.bat` → Option 3 (Restart Bot)
2. `dev.bat` → Option 5 (View Logs)

### **For Full Updates:**
1. `dev.bat` → Option 13 (Complete update)
2. OR run `update.bat` for production-style update

## 🔍 **File Structure After Fix**

```
MalaBoT/
├── bot.py                 # Main bot file
├── dev.bat               # ✅ FIXED: Complete development tool
├── dev_simple.bat         # Simple version (backup)
├── dev_original_backup.bat # Original dev.bat (backup)
├── diagnose.bat           # ✅ NEW: Diagnostic tool
├── update.bat             # ✅ EXPLAINED: Production update script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your actual config (create this)
├── data/                 # ✅ AUTO-CREATED: Bot data directory
│   └── logs/             # ✅ AUTO-CREATED: Log files
├── backups/              # ✅ AUTO-CREATED: Backup storage
├── cogs/                 # Bot commands
├── config/               # Configuration files
├── database/             # Database models
└── utils/                # Utility functions
```

## 💡 **Pro Tips**

1. **Always run `diagnose.bat`** if you're having issues
2. **Use option 17** to test configuration before starting bot
3. **Use option 5** to see real-time logs when debugging
4. **Use option 13** for safe updates (it validates everything)
5. **Keep your .env file secure** - never commit it to git!

## 🆘 **Getting Help**

If you still have issues:
1. Run `diagnose.bat` - it will tell you exactly what's wrong
2. Check the live logs with option 5
3. Test configuration with option 17
4. Look at recent log entries in option 4 status display

The fixed system now provides **complete visibility** into what's happening with your bot, so you'll never run in circles trying to find problems again!

## 🎉 **You're All Set!**

Your MalaBoT development environment is now **completely fixed** and includes:
- ✅ Proper error handling and logging
- ✅ Automatic directory creation
- ✅ Configuration validation
- ✅ Live log viewing
- ✅ Comprehensive diagnostic tools
- ✅ Professional development workflows

Happy coding with MalaBoT! 🤖