@echo off
REM FIXED Development Script for MalaBoT
REM This script handles the complete local development workflow

setlocal enabledelayedexpansion
chcp 65001 >nul

REM Set window title
title MalaBoT Development Tools

REM Configure git to never open editor for merges
git config pull.rebase false >nul 2>&1
git config merge.commit no >nul 2>&1
git config core.editor "echo" >nul 2>&1

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo [INFO] Checking dependencies...
pip show discord.py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Create necessary directories
if not exist "data" mkdir "data"
if not exist "data\logs" mkdir "data\logs"
if not exist "backups" mkdir "backups"

:menu
cls
echo ================================================================================
echo                          MalaBoT Development Tools
echo ================================================================================
echo [LOCAL BOT MANAGEMENT]
echo  1. Start Local Bot              - Clear cache, validate config, start bot
echo  2. Stop Bot(s)                   - Stop all bot processes including droplet
echo  3. Start Droplet Bot            - Deploy and start on production
echo  4. Check Local Status           - View status, logs, process info
echo  5. Check Droplet Status         - View PM2 status on droplet
echo  6. View Live Logs               - Real-time log monitoring (Ctrl+C to exit)
echo  7. View Droplet Logs            - View live logs from droplet
echo.
echo [GIT OPERATIONS]
echo  8. Check Git Status             - View modified/staged files
echo  9. Stage All Changes            - Stage all files for commit
echo 10. Commit Changes               - Commit staged files with message
echo 11. Preview GitHub Changes       - See what will be pulled before pulling
echo 12. Pull from GitHub             - Get latest changes from remote
echo.
echo [EXIT]
echo  0. Exit                         - Close development tools
echo.
echo ================================================================================
set /p choice="Enter your choice: "

if `"%choice%`"==`"1`" goto start
if `"%choice%`"==`"2`" goto stop
if `"%choice%`"==`"3`" goto quick_deploy
if `"%choice%`"==`"4`" goto status
if `"%choice%`"==`"5`" goto droplet_status
if `"%choice%`"==`"6`" goto logs
if `"%choice%`"==`"7`" goto droplet_logs
if `"%choice%`"==`"8`" goto gitstatus
if `"%choice%`"==`"9`" goto gitstage
if `"%choice%`"==`"10`" goto gitcommit
if `"%choice%`"==`"11`" goto gitpreview
if `"%choice%`"==`"12`" goto gitpull
if `"%choice%`"==`"0`" goto exit

echo Invalid choice. Please try again.
timeout /T 2 /NOBREAK >NUL
goto menu

:start
echo.
echo [1/4] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [2/4] Checking for .env file...
if not exist .env (
    echo [WARNING] .env file not found!
    echo [INFO] Creating from template...
    if exist .env.example (
        copy .env.example .env >NUL
        echo [INFO] .env file created from template!
        echo [IMPORTANT] Please edit .env file with your bot token and settings:
        echo          - DISCORD_TOKEN: Your Discord bot token
        echo          - OWNER_IDS: Your Discord user ID
        pause
        goto menu
    ) else (
        echo [ERROR] .env.example file not found!
        pause
        goto menu
    )
)

echo [3/4] Testing configuration...
python -c "from src.config.settings import settings; errors = settings.validate(); print('Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Configuration test failed!
    echo [INFO] Please check your .env file and ensure:
    echo        - DISCORD_TOKEN is set correctly
    echo        - OWNER_IDS contains your Discord user ID
    pause
    goto menu
)

echo [4/4] Starting MalaBoT...
start "MalaBoT Console" cmd /k "title MalaBoT Console && python bot.py"
echo [SUCCESS] Bot started in new window!
echo [INFO] Use option 4 to view live logs
timeout /T 3 /NOBREAK >NUL
goto menu

:stop
echo.
echo [INFO] Stopping ALL MalaBoT processes...

REM Kill ALL python.exe processes (including ghosts)
echo [1/2] Terminating all Python processes...
taskkill /IM python.exe /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] All Python processes terminated
) else (
    echo [INFO] No Python processes found
)

REM Double-check and kill any remaining bot processes
echo [2/2] Verifying cleanup...
timeout /T 1 /NOBREAK >nul
tasklist /FI "IMAGENAME eq python.exe" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Some Python processes still running, forcing termination...
    taskkill /F /IM python.exe /T >nul 2>&1
)

echo [SUCCESS] All bot processes stopped
echo.
echo [3/3] Stopping droplet bot...
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 stop malabot" 2>nul
if 0 EQU 0 (
    echo [SUCCESS] Droplet bot stopped
) else (
    echo [INFO] Droplet bot may not be running or already stopped
)
  echo [4/4] Flushing droplet PM2 logs...
  ssh %DROPLET_USER%@%DROPLET_IP% "pm2 flush malabot" 2>nul
  if 0 EQU 0 (
      echo [SUCCESS] Droplet logs flushed
  ) else (
      echo [INFO] Could not flush logs
  )
timeout /T 2 /NOBREAK >nul
goto menu

:status
echo.
echo ========================================
echo Bot Status:
echo ========================================

REM Safe timestamp
for /f "tokens=2 delims==." %%A in ('wmic os get localdatetime /value 2^>nul') do set "ts_raw=%%A"
if not defined ts_raw (
    set "ts=Unknown"
) else (
    set "ts=%ts_raw:~0,4%-%ts_raw:~4,2%-%ts_raw:~6,2% %ts_raw:~8,2%:%ts_raw:~10,2%"
)
echo Checked: %ts%
echo ========================================

REM Check if bot window is running
tasklist /V /FI "WINDOWTITLE eq MalaBoT Console" 2>nul | find /I "MalaBoT Console" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Bot is RUNNING via window title
    goto status_done
)

REM Check if python processes are running bot.py
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "bot.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Bot is RUNNING via process detection
    echo Running processes:
    tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "bot.py"
    goto status_done
)

echo [STATUS] Bot is NOT RUNNING

:status_done
echo.
echo ========================================
echo Recent log entries (last 10 lines):
echo ========================================

if exist "data\logs\bot.log" (
    echo [INFO] Displaying last 10 log lines...
    for /f "skip=-10" %%L in ('type "data\logs\bot.log" 2^>nul') do echo %%L
) else (
    echo [INFO] No log file found - bot may not have started yet
)

echo ========================================
echo.
pause
goto menu

:logs
echo.
echo [INFO] Opening log viewer...
echo [INFO] Press Ctrl+C to stop viewing logs
echo.

if exist "data\logs\bot.log" (
    type "data\logs\bot.log" | more
) else (
    echo [WARNING] Log file not found at: data\logs\bot.log
    echo [INFO] Check if bot is running
)
pause
goto menu

:quick_deploy
echo.
echo ========================================
echo Quick Deploy (All-in-One)
echo ========================================
echo.
echo This will:
echo   1. Stage all changes
echo   2. Commit with your message
echo   3. Push to GitHub
echo   4. Deploy to droplet
echo   5. Restart bot on droplet
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo [CANCELLED] Quick deploy cancelled.
    pause
    goto menu
)

call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)

echo [1/6] Staging all changes...
git add .

echo [2/6] Enter commit message:
set /p message="Commit message: "
if "%message%"=="" (
    echo [ERROR] Commit message cannot be empty!
    pause
    goto menu
)

echo [3/6] Committing changes...
git commit -m "%message%"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] No changes to commit or commit failed
)

echo [4/6] Pushing to GitHub branch: %current_branch%...
git push origin %current_branch%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to push to GitHub!
    pause
    goto menu
)

echo [5/6] Deploying to droplet...
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
set DROPLET_DIR=/home/malabot/MalaBoT

ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && git fetch origin && git checkout %current_branch% && git reset --hard origin/%current_branch%"

echo [6/6] Restarting bot on droplet...
ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && pip3 install -r requirements.txt --quiet && pm2 restart malabot"

echo.
echo ========================================
echo [SUCCESS] Quick Deploy Complete!
echo ========================================
echo.
echo Your changes are now live on the droplet!
echo.
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 list && pm2 logs malabot --lines 10 --nostream"
echo.
pause
goto menu


:droplet_stop
echo.
echo ========================================
echo Stop Droplet Bot
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
echo.
echo WARNING: This will stop the bot on the droplet!
set /p confirm="Are you sure? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    goto menu
)
echo Stopping bot on droplet...
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 stop malabot"
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot stopped
    ssh %DROPLET_USER%@%DROPLET_IP% "pm2 list"
) else (
    echo [ERROR] Failed to stop bot
)
echo.
pause
goto menu

:droplet_status
echo.
echo ========================================
echo Droplet Status (PM2)
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
echo Checking bot status on droplet...
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 list && echo. && pm2 info malabot"
echo.
pause
goto menu

:droplet_logs
echo.
echo ========================================
echo Droplet Logs (Live)
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
echo Viewing live logs from droplet...
echo Press Ctrl+C to stop viewing logs
echo.
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 logs malabot"
goto menu

:gitstatus
echo.
echo ========================================
echo Git Status:
echo ========================================
git status
echo.
echo ========================================
pause
goto menu

:gitstage
echo.
echo [INFO] Staging all changes...
git add .
echo [SUCCESS] All changes staged!
echo.
echo Staged files:
git status --short
timeout /T 3 /NOBREAK >NUL
goto menu

:gitcommit
echo.
set /p message="Enter commit message: "
if "%message%"=="" (
    echo [ERROR] Commit message cannot be empty!
    timeout /T 2 /NOBREAK >NUL
    goto menu
)
echo [INFO] Committing changes...
git commit -m "%message%"
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Changes committed!
) else (
    echo [INFO] No changes to commit or commit failed
)
timeout /T 3 /NOBREAK >NUL
goto menu


:gitpreview
echo.
echo ========================================
echo Preview GitHub Changes
echo ========================================
call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)
echo Fetching latest changes from GitHub...
git fetch origin %current_branch%
echo.
echo Changes that will be pulled:
git log HEAD..origin/%current_branch% --oneline
echo.
echo Files that will be changed:
git diff --name-status HEAD..origin/%current_branch%
echo.
set /p proceed=Pull these changes? (y/n): 
if /i "%proceed%"=="y" goto gitpull
echo [CANCELLED] Pull cancelled.
pause
goto menu

:gitpull
echo.
echo [INFO] Pulling from GitHub...
call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)
echo [INFO] Pulling latest changes for branch: %current_branch%
echo.
git pull origin %current_branch%
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Pulled from GitHub successfully!
) else (
    echo.
    echo [ERROR] Failed to pull from GitHub. Your local changes might conflict.
    echo [INFO] Use 'git status' to see conflicting files.
)
echo.
pause
goto menu

:get_current_branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set "current_branch=%%i"
goto :eof

:exit
echo.
echo [INFO] Thank you for using MalaBoT Development Tools!
echo.
pause
exit /b 0
