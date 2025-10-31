# Windows Commands for Bot Management

## Restarting the Bot on Windows

### Method 1: Using Task Manager (Easiest)
1. Press `Ctrl + Shift + Esc` to open Task Manager
2. Go to "Details" tab
3. Find `python.exe` or `python3.exe`
4. Right-click → "End Task"
5. Open Command Prompt in bot directory
6. Run: `python bot.py`

### Method 2: Using Command Prompt
```cmd
# Find Python processes
tasklist | findstr python

# Kill specific process (replace PID with actual number)
taskkill /PID <process_id> /F

# Start bot
python bot.py
```

### Method 3: Using PowerShell (Recommended)
```powershell
# Kill all Python processes
Get-Process python* | Stop-Process -Force

# Start bot in background
Start-Process python -ArgumentList "bot.py" -WindowStyle Hidden

# Or start in new window
Start-Process python -ArgumentList "bot.py"
```

## Quick Restart Script

Create a file called `restart_bot.bat`:

```batch
@echo off
echo Stopping bot...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM python3.exe 2>nul
timeout /t 2 /nobreak >nul
echo Starting bot...
start /B python bot.py
echo Bot restarted!
```

Then just run: `restart_bot.bat`

## Checking if Bot is Running

```cmd
# Check for Python processes
tasklist | findstr python

# Check bot logs
type data\logs\bot.log | more
```

## Running Scripts

### Check Database
```cmd
python check_database_settings.py
```

### Fix Database
```cmd
python fix_database_settings.py 542004156513255445
```

### Cleanup Old XP Keys
```cmd
python cleanup_old_xp_keys.py 542004156513255445
```

## Common Issues

### "The process cannot access the file"
**Cause:** Bot is already running

**Solution:**
1. Kill Python process via Task Manager
2. Wait 5 seconds
3. Try again

### "python is not recognized"
**Cause:** Python not in PATH

**Solution:**
```cmd
# Use full path
C:\Users\malak\AppData\Local\Programs\Python\Python311\python.exe bot.py

# Or add to PATH in System Environment Variables
```

### Bot Crashes Immediately
**Cause:** Missing dependencies or config error

**Solution:**
```cmd
# Check logs
type data\logs\bot.log

# Reinstall dependencies
pip install -r requirements.txt
```

## Development Workflow

### 1. Pull Latest Changes
```cmd
git pull origin main
```

### 2. Stop Bot
```cmd
taskkill /F /IM python.exe
```

### 3. Run Fixes (if needed)
```cmd
python fix_database_settings.py 542004156513255445
python cleanup_old_xp_keys.py 542004156513255445
```

### 4. Start Bot
```cmd
python bot.py
```

### 5. Check Logs
```cmd
type data\logs\bot.log
```

## Useful Aliases

Add these to a `aliases.bat` file:

```batch
@echo off

if "%1"=="start" (
    python bot.py
) else if "%1"=="stop" (
    taskkill /F /IM python.exe
) else if "%1"=="restart" (
    taskkill /F /IM python.exe
    timeout /t 2 /nobreak >nul
    python bot.py
) else if "%1"=="logs" (
    type data\logs\bot.log
) else if "%1"=="check" (
    python check_database_settings.py
) else (
    echo Usage: aliases [start^|stop^|restart^|logs^|check]
)
```

Then use:
```cmd
aliases start
aliases stop
aliases restart
aliases logs
aliases check
```