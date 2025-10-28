# dev.bat Complete Reference Guide

## 🎯 Quick Start
Run `dev.bat` and choose an option by typing the number and pressing Enter.

---

## 📋 ALL OPTIONS EXPLAINED

### 🤖 BOT MANAGEMENT

#### **Option 1: Start Bot (with cache clear)**
- **What it does:** Clears Python cache, checks .env file, validates config, starts bot in new window
- **When to use:** Starting the bot for the first time or after making changes
- **Output:** Opens new console window titled "MalaBoT Console"
- **Time:** ~5 seconds

#### **Option 2: Stop Bot**
- **What it does:** Stops the bot using multiple methods (window title → process detection → fallback)
- **When to use:** When you need to stop the bot to make changes or restart
- **Methods:** 
  1. Closes by window title "MalaBoT Console"
  2. Finds and kills python processes running bot.py
  3. Fallback termination if needed
- **Time:** ~2 seconds

#### **Option 3: Restart Bot (with cache clear)**
- **What it does:** Stops bot → Clears cache → Tests config → Starts bot
- **When to use:** After making code changes or when bot is acting weird
- **Time:** ~10 seconds

#### **Option 4: Check Bot Status**
- **What it does:** Shows if bot is running, displays recent logs (last 10 lines), shows timestamp
- **When to use:** To verify bot is running or check for errors
- **Shows:**
  - Bot running status (RUNNING/NOT RUNNING)
  - Process information
  - Last 10 log entries
  - Current timestamp
- **Time:** Instant

#### **Option 5: View Live Logs**
- **What it does:** Opens live log viewer showing real-time bot activity
- **When to use:** Debugging issues or monitoring bot activity
- **How to exit:** Press Ctrl+C
- **Shows:** Last 20 lines + new entries as they happen
- **Time:** Continuous until stopped

#### **Option 6: Clear All Caches**
- **What it does:** Clears Python cache, pytest cache, temp files, old logs (keeps last 5)
- **When to use:** When bot is acting weird or before major updates
- **Clears:**
  - .pyc files
  - __pycache__ directories
  - .pytest_cache
  - *.tmp, *.log, *.bak files
  - Old log files (keeps 5 most recent)
- **Time:** ~3 seconds

---

### 🔄 WORKFLOWS

#### **Option 7: Update Workflow**
- **What it does:** Pull from GitHub → Install dependencies → Restart bot → Check status → Show logs
- **When to use:** Updating bot with latest changes from GitHub
- **Steps:**
  1. Pulls latest code from GitHub
  2. Installs/updates dependencies
  3. Restarts bot
  4. Checks status
  5. Opens logs
- **Time:** ~30 seconds
- **Requires:** Internet connection, GitHub access

#### **Option 8: Deploy Workflow**
- **What it does:** Stage changes → Commit → Push to GitHub
- **When to use:** Saving your local changes to GitHub
- **Steps:**
  1. Shows git status
  2. Asks to stage all changes (Y/N)
  3. Asks for commit message
  4. Commits changes
  5. Pushes to GitHub
- **Time:** ~10 seconds
- **Requires:** Git configured, GitHub access

---

### 🔧 GIT OPERATIONS

#### **Option 9: Check Git Status**
- **What it does:** Shows current git status (modified files, staged changes, branch info)
- **When to use:** Before committing to see what changed
- **Shows:**
  - Current branch
  - Modified files
  - Staged changes
  - Untracked files
- **Time:** Instant

#### **Option 10: Stage All Changes**
- **What it does:** Stages all modified and new files for commit
- **When to use:** Before committing changes
- **Command:** `git add .`
- **Time:** Instant

#### **Option 11: Commit Changes**
- **What it does:** Commits staged changes with your message
- **When to use:** After staging changes (option 10)
- **Asks for:** Commit message
- **Time:** Instant

#### **Option 12: Push to GitHub**
- **What it does:** Pushes committed changes to GitHub
- **When to use:** After committing (option 11) to backup/share code
- **Steps:**
  1. Pulls remote changes (auto-merge)
  2. Pushes your commits
- **Time:** ~5 seconds
- **Requires:** GITHUB_TOKEN environment variable (optional but recommended)

#### **Option 13: Remote Deploy to Droplet**
- **What it does:** Pushes to GitHub → SSH to droplet → Pull changes → Restart bot → Show logs
- **When to use:** Deploying to production server
- **Steps:**
  1. Pushes local changes to GitHub
  2. SSHs into droplet (165.232.156.230)
  3. Pulls latest code
  4. Restarts bot on server
  5. Shows remote logs
- **Time:** ~20 seconds
- **Requires:** SSH access to droplet, GITHUB_TOKEN

#### **Option 14: Pull from GitHub**
- **What it does:** Downloads latest changes from GitHub to your local machine
- **When to use:** Getting updates made by others or from another computer
- **Command:** `git pull origin main`
- **Time:** ~5 seconds
- **Important:** This is what you use to get my fixes!

#### **Option 15: View Commit History**
- **What it does:** Shows last 10 commits with messages
- **When to use:** Checking recent changes or finding when something changed
- **Shows:** Commit hash, message, author, date
- **Time:** Instant

---

### 🛠️ UTILITIES

#### **Option 16: Install/Update Dependencies**
- **What it does:** Installs or updates all Python packages from requirements.txt
- **When to use:** First setup, after pulling updates, or when packages are outdated
- **Command:** `pip install -r requirements.txt`
- **Time:** ~30 seconds (first time), ~5 seconds (updates)

#### **Option 17: Create .env File from Template**
- **What it does:** Creates .env file from .env.example or creates basic template
- **When to use:** First setup or if .env is deleted/corrupted
- **Asks:** Overwrite if .env already exists
- **Creates:** .env with template values
- **Important:** You must edit .env with your bot token and settings!
- **Time:** Instant

#### **Option 18: Test Bot Configuration**
- **What it does:** Validates .env file and checks for configuration errors
- **When to use:** After editing .env or troubleshooting startup issues
- **Checks:**
  - .env file exists
  - Required settings present
  - Settings format valid
- **Shows:** Configuration details or error messages
- **Time:** Instant

---

### ⚙️ ADVANCED OPS

#### **Option 19: Full Local Clean Update**
- **What it does:** Complete clean update with backup
- **When to use:** Major updates or when things are broken
- **Steps:**
  1. Stops bot
  2. Backs up logs and database
  3. Git reset --hard (discards local changes)
  4. Pulls from GitHub
  5. Installs dependencies
  6. Clears caches
  7. Restarts bot
  8. Checks status
- **Time:** ~60 seconds
- **Warning:** Discards uncommitted local changes!

#### **Option 20: Backup Now**
- **What it does:** Creates timestamped backup of logs and database
- **When to use:** Before major changes or regularly for safety
- **Backs up:**
  - data/logs/ → backups/logs/YYYY-MM-DD_HH-MM/
  - data/bot.db → backups/db/bot_YYYY-MM-DD_HH-MM.db
- **Time:** ~2 seconds
- **Location:** backups/ folder

#### **Option 21: Verify Environment**
- **What it does:** Validates .env file and configuration
- **When to use:** Troubleshooting startup issues
- **Checks:** Same as option 18 but more detailed
- **Time:** Instant

#### **Option 22: Clear All (Commands + Caches + Logs + Temp)**
- **What it does:** COMPLETE system cleanup
- **When to use:** When commands aren't working or bot is acting weird
- **Steps:**
  1. Stops bot
  2. Runs cleanup.py (clears caches, temp files, old logs)
  3. Runs clear_and_sync.py (clears Discord commands)
  4. Verifies completion
- **Clears:**
  - Discord slash commands (all servers)
  - Python cache
  - Pytest cache
  - Temporary files
  - Old logs (keeps 5)
  - Discord.py cache
- **Time:** ~30 seconds
- **Asks:** Confirmation (yes/y)
- **Important:** Bot needs to restart after this!

#### **Option 23: Fix /verify Command Structure**
- **What it does:** Fixes /verify to show as parent command with subcommands
- **When to use:** When /verify shows as 4 separate commands instead of 1 parent
- **Steps:**
  1. Stops bot
  2. Clears all Discord commands
  3. Reloads verify cog properly
  4. Syncs with correct structure
- **Result:** /verify appears as ONE command with THREE subcommands (submit, review, setup)
- **Time:** ~30 seconds
- **Asks:** Confirmation (yes/y)
- **After:** Wait 30 seconds, then test in Discord

---

### 🚪 EXIT

#### **Option 0: Exit**
- **What it does:** Closes dev.bat
- **When to use:** When you're done
- **Time:** Instant

---

## 🎯 COMMON WORKFLOWS

### **First Time Setup:**
```
1. Option 16 (Install Dependencies)
2. Option 17 (Create .env File)
3. Edit .env with your bot token
4. Option 18 (Test Configuration)
5. Option 1 (Start Bot)
```

### **Daily Development:**
```
1. Option 14 (Pull from GitHub) - Get latest changes
2. Option 3 (Restart Bot) - Apply changes
3. Make your changes
4. Option 10 (Stage Changes)
5. Option 11 (Commit Changes)
6. Option 12 (Push to GitHub)
```

### **Commands Not Working:**
```
1. Option 22 (Clear All)
2. Option 23 (Fix /verify)
3. Option 1 (Start Bot)
4. Wait 30 seconds
5. Test in Discord
```

### **Bot Acting Weird:**
```
1. Option 4 (Check Status)
2. Option 5 (View Logs) - Check for errors
3. Option 6 (Clear Caches)
4. Option 3 (Restart Bot)
```

### **Deploy to Production:**
```
1. Option 8 (Deploy Workflow) - Push to GitHub
2. Option 13 (Remote Deploy) - Deploy to droplet
```

---

## 💡 PRO TIPS

1. **Always check status (option 4) before assuming bot is down**
2. **Use option 5 (logs) to debug issues - errors show there**
3. **Option 22 (Clear All) fixes most command issues**
4. **Option 14 (Pull) before option 12 (Push) to avoid conflicts**
5. **Option 20 (Backup) before option 19 (Full Clean Update)**
6. **Option 23 fixes /verify command structure issues**
7. **Use option 7 (Update Workflow) for quick updates**
8. **Option 18 (Test Config) before starting bot saves time**

---

## 🆘 TROUBLESHOOTING

**Bot won't start:**
- Option 18 (Test Configuration)
- Check .env file has correct token
- Option 5 (View Logs) for error details

**Commands not showing in Discord:**
- Option 22 (Clear All)
- Option 23 (Fix /verify)
- Wait 30 seconds
- Restart Discord (Ctrl+R)

**Git push fails:**
- Option 14 (Pull from GitHub) first
- Then option 12 (Push to GitHub)
- Set GITHUB_TOKEN if needed

**Bot running but not responding:**
- Option 4 (Check Status)
- Option 5 (View Logs)
- Option 3 (Restart Bot)

---

## 📝 NOTES

- All options are safe to use
- Options that modify files ask for confirmation
- Logs are always preserved (except option 6 keeps last 5)
- Database is backed up automatically in workflows
- Git operations require internet connection
- Remote deploy requires SSH access to droplet

---

**Last Updated:** 2025-10-28
**Version:** 2.0