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
echo.
echo [BOT MANAGEMENT]
echo  1. Start Bot                    - Clear cache, validate config, start bot
echo  2. Stop Bot                     - Stop running bot (multi-method)
echo  3. Restart Bot                  - Stop, clear cache, restart bot
echo  4. Check Bot Status             - View status, logs, process info
echo  5. View Live Logs               - Real-time log monitoring (Ctrl+C to exit)
echo  6. Clear All Caches             - Clear Python/pytest/temp caches
echo.
echo [WORKFLOWS]
echo  7. Update Workflow              - Pull + Install + Restart + Status
echo  8. Deploy Workflow              - Stage + Commit + Push to GitHub
echo.
echo [GIT OPERATIONS]
echo  9. Check Git Status             - View modified/staged files
echo 10. Stage All Changes            - Stage all files for commit
echo 11. Commit Changes               - Commit staged files with message
echo 12. Push to GitHub               - Push commits to remote
echo 13. Remote Deploy to Droplet    - Deploy to production server (PM2)
echo 14. Pull from GitHub             - Get latest changes from remote
echo 15. View Commit History          - Show last 10 commits
echo.
echo [DROPLET MANAGEMENT]
echo 16. View Droplet Status          - Check PM2 bot status on droplet
echo 17. View Droplet Logs            - View live logs from droplet
echo 18. Restart Droplet Bot          - Restart bot on droplet
echo 19. Stop Droplet Bot             - Stop bot on droplet
echo.
echo [UTILITIES]
echo 20. Install Dependencies         - Install/update Python packages
echo 21. Test Configuration           - Validate .env settings
echo.
echo [ADVANCED OPS]
echo 22. Backup Now                   - Backup logs and database
echo 23. Verify Environment           - Check configuration validity
echo 24. Clear All                    - Clear commands + caches + logs + temp
echo 25. Sync DB from Droplet        - Download latest database from production
echo 26. Sync DB to Droplet          - Upload local database to production
echo 27. Quick Deploy                 - Commit + Push + Deploy to Droplet (all-in-one)
echo.
echo [EXIT]
echo  0. Exit                         - Close development tools

echo.
echo ================================================================================
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto clearcache
if "%choice%"=="7" goto updateworkflow
if "%choice%"=="8" goto deployworkflow
if "%choice%"=="9" goto gitstatus
if "%choice%"=="10" goto gitstage
if "%choice%"=="11" goto gitcommit
if "%choice%"=="12" goto gitpush
if "%choice%"=="13" goto remotedeploy
if "%choice%"=="14" goto gitpull
if "%choice%"=="15" goto githistory
if "%choice%"=="16" goto droplet_status
if "%choice%"=="17" goto droplet_logs
if "%choice%"=="18" goto droplet_restart
if "%choice%"=="19" goto droplet_stop
if "%choice%"=="20" goto installdeps
if "%choice%"=="21" goto testconfig
if "%choice%"=="22" goto backupnow
if "%choice%"=="23" goto verifyenv
if "%choice%"=="24" goto clearall
if "%choice%"=="25" goto sync_db_from_droplet
if "%choice%"=="26" goto sync_db_to_droplet
if "%choice%"=="27" goto quick_deploy
if "%choice%"=="0" goto exit


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
python -c "from config.settings import settings; errors = settings.validate(); print('Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
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
echo [INFO] Use option 5 to view live logs
timeout /T 3 /NOBREAK >NUL
goto menu

:stop
echo.
echo [INFO] Stopping MalaBoT...

REM Method 1: Try to close by window title
echo [1/3] Attempting to stop via window title...
taskkill /FI "WINDOWTITLE eq MalaBoT Console" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot stopped via window title
    goto stop_done
)

REM Method 2: Try to find and kill python processes running bot.py
echo [2/3] Attempting to stop via process detection...
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "bot.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2 delims=," %%P in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "bot.py"') do (
        taskkill /PID %%P /F >nul 2>&1
    )
    echo [SUCCESS] Bot stopped via process detection
    goto stop_done
)

REM Method 3: Fallback - try all python processes
echo [3/3] Attempting fallback termination...
taskkill /IM python.exe /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot stopped via fallback method
    goto stop_done
)

echo [WARNING] Could not find running bot process
:stop_done
timeout /T 2 /NOBREAK >nul
goto menu

:restart
echo.
echo [1/5] Stopping bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL

echo [2/5] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [3/5] Testing configuration...
if not exist .env (
    echo [ERROR] .env file missing! Use option 16 to create it.
    pause
    goto menu
)

python -c "from config.settings import settings; errors = settings.validate(); print('Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Configuration test failed!
    echo [INFO] Check your .env file settings
    pause
    goto menu
)

echo [4/5] Starting bot...
start "MalaBoT Console" cmd /k "title MalaBoT Console && python bot.py"

echo [5/5] Bot restarted successfully!
echo [INFO] Use option 5 to view live logs
timeout /T 3 /NOBREAK >NUL
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

:clearcache
echo.
echo [INFO] Clearing all caches...
echo [1/4] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [2/4] Clearing pytest cache...
rmdir /S /Q .pytest_cache 2>NUL

echo [3/4] Cleaning temporary files...
del /F /Q *.tmp 2>NUL

echo [4/4] Cleaning old logs (keeping last 5)...
if exist "data\logs\*.log" (
    dir /B /O-D "data\logs\*.log" 2>nul > temp_files.txt
    for /f "skip=5 delims=" %%F in (temp_files.txt) do del "data\logs\%%F" 2>NUL
    del temp_files.txt 2>NUL
)

echo [SUCCESS] All caches cleared!
timeout /T 2 /NOBREAK >NUL
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

:gitpush
echo.
echo [INFO] Pushing to GitHub...
call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)
echo [INFO] Pushing to branch: %current_branch%
git push origin %current_branch%
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pushed to GitHub successfully!
) else (
    echo [ERROR] Failed to push to GitHub.
    echo [INFO] 1. Check if you have new remote changes by running 'git pull'.
    echo [INFO] 2. Check if you have committed your local changes.
    echo [INFO] 3. Check your network connection and git credentials.
)
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

:githistory
echo.
echo ========================================
echo Last 10 Commits:
echo ========================================
git log --oneline -10
echo.
echo ========================================
pause
goto menu

:updateworkflow
echo.
echo ========================================
echo Starting Update Workflow
echo ========================================
echo.
call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)

echo [1/5] Pulling latest changes for branch %current_branch%...
git pull origin %current_branch%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull from GitHub!
    pause
    goto menu
)

echo [2/5] Installing dependencies...
call :installdeps_silent

echo [3/5] Restarting bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL
call :start_internal

echo [4/5] Checking status...
timeout /T 3 /NOBREAK >NUL
call :status_basic

echo [5/5] Workflow complete!
echo ========================================
echo [SUCCESS] Update Workflow Complete!
echo ========================================
pause
goto menu

:deployworkflow
echo.
echo ========================================
echo Starting Deploy Workflow
echo ========================================
echo.
call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)

echo [1/5] Checking git status...
git status --short
echo.

set /p confirm="Do you want to stage all changes? (Y/N): "
if /i not "%confirm%"=="Y" goto menu

echo [2/5] Staging changes...
git add .

echo [3/5] Enter commit message:
set /p message="Commit message: "
if "%message%"=="" (
    echo [ERROR] Commit message cannot be empty!
    timeout /T 2 /NOBREAK >NUL
    goto menu
)

echo [4/5] Committing changes...
git commit -m "%message%"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to commit changes!
    pause
    goto menu
)

echo [5/5] Pushing to GitHub branch: %current_branch%...
git push origin %current_branch%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Deploy Workflow Complete!
    echo ========================================
    echo.
    echo Your changes are now on GitHub!
    echo.
) else (
    echo [ERROR] Failed to push to GitHub
)

pause
goto menu

:installdeps
echo.
echo [INFO] Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Dependencies installed successfully!
) else (
    echo [ERROR] Failed to install dependencies!
)
timeout /T 3 /NOBREAK >NUL
goto menu

:installdeps_silent
pip install -r requirements.txt >nul 2>&1
goto :eof

:testconfig
echo.
echo [INFO] Testing bot configuration...
if not exist .env (
    echo [ERROR] .env file not found! Create .env file first.
    pause
    goto menu
)

python -c "try:
    from config.settings import settings
    errors = settings.validate()
    if errors:
        print('[ERROR] Configuration errors:')
        for error in errors:
            print(f'  - {error}')
    else:
        print('[SUCCESS] Configuration is valid!')
        print(f'[INFO] Bot Name: {settings.BOT_NAME}')
        print(f'[INFO] Bot Prefix: {settings.BOT_PREFIX}')
        print(f'[INFO] Log Level: {settings.LOG_LEVEL}')
        print(f'[INFO] Log File: {settings.LOG_FILE}')
except Exception as e:
    print(f'[ERROR] Failed to load configuration: {e}')
"

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Configuration test failed!
) else (
    echo [SUCCESS] Configuration test completed!
)
pause
goto menu

:remotedeploy
echo.
echo ========================================
echo Remote Deploy to Droplet (PM2)
echo ========================================
call :get_current_branch
if not defined current_branch (
    echo [ERROR] Could not determine the current Git branch.
    pause
    goto menu
)
if not "%current_branch%"=="main" (
    echo [WARNING] You are not on the 'main' branch.
    set /p confirm_deploy="Are you sure you want to deploy the '%current_branch%' branch? (y/n): "
    if /i not "%confirm_deploy%"=="y" (
        echo [CANCELLED] Remote deploy cancelled.
        pause
        goto menu
    )
)

set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
set DROPLET_DIR=/home/malabot/MalaBoT

echo [1/8] Pushing local changes to GitHub branch %current_branch%...
git push origin %current_branch%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git push failed. Make sure changes are committed first.
    pause
    goto menu
)

echo [2/8] SSH into droplet and update code...
ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && git fetch origin && git checkout %current_branch% && git reset --hard origin/%current_branch%"

echo [3/8] Stopping bot on droplet...
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 stop malabot"

echo [4/8] Syncing local database to droplet...
scp data\bot.db %DROPLET_USER%@%DROPLET_IP%:%DROPLET_DIR%/data/bot.db

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Database sync failed - droplet will use existing database
)

echo [5/8] Installing/updating dependencies...
ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && pip3 install -r requirements.txt --quiet"

echo [6/8] Clearing Python cache...
ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null; find . -type f -name '*.pyc' -delete"

echo [7/8] Restarting bot with PM2...

ssh %DROPLET_USER%@%DROPLET_IP% "pm2 restart malabot || pm2 start %DROPLET_DIR%/bot.py --name malabot --interpreter python3"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to restart bot with PM2
    pause
    goto menu
)

echo [8/8] Checking bot status...

ssh %DROPLET_USER%@%DROPLET_IP% "pm2 list && pm2 logs malabot --lines 20 --nostream"
echo.
echo [SUCCESS] Remote deploy complete!
echo Bot is running on droplet with PM2
echo Database synced from local to droplet
echo.

pause
goto menu


:backupnow
echo.
echo ========================================
echo Backup Now
echo ========================================

REM Safe universal timestamp
for /f "tokens=2 delims==." %%A in ('wmic os get localdatetime /value 2^>nul') do set "dt=%%A"
set "TS=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%"

if not exist "backups\logs" mkdir "backups\logs"
if not exist "backups\db" mkdir "backups\db"
if exist "data\logs" xcopy "data\logs" "backups\logs\%TS%\" /E /Q /Y >nul
if exist "data\bot.db" copy /Y "data\bot.db" "backups\db\bot_%TS%.db" >nul
echo [SUCCESS] Backup saved with tag %TS%.
pause
goto menu

:verifyenv
echo.
echo ========================================
echo Verify Environment
echo ========================================
if not exist .env (
    echo [ERROR] .env not found!
    pause
    goto menu
)

python -c "from config.settings import settings; errs=settings.validate(); import sys; sys.exit(0) if not errs else (print('[ERROR] Config validation failed:') or [print(' -', e) for e in errs] or sys.exit(1))"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Environment validated successfully.
) else (
    echo [ERROR] Validation failed. Check your .env settings.
)
pause
goto menu

:clearall
echo.
echo ========================================
echo Clear All - Complete System Cleanup
echo ========================================
echo.
echo [WARNING] This will clear:
echo   - Discord slash commands (all servers)
echo   - Python cache files (.pyc, __pycache__)
echo   - Pytest cache
echo   - Temporary files
echo   - Old log files (keeping last 5)
echo   - Discord.py cache
echo.
set /p confirm="Are you sure you want to continue? (yes/no): "
if /i "%confirm%"=="yes" goto clearall_continue
if /i "%confirm%"=="y" goto clearall_continue
echo [CANCELLED] Clear all operation cancelled.
timeout /T 2 /NOBREAK >NUL
goto menu

:clearall_continue

echo.
echo [1/4] Stopping bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL

echo [2/4] Running system cleanup...
python cleanup.py --auto
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Cleanup script encountered errors
) else (
    echo [SUCCESS] System cleanup completed
)

echo [3/4] Clearing Discord commands...
python clear_and_sync.py --auto
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Command clear script failed or was cancelled
) else (
    echo [SUCCESS] Discord commands cleared
)

echo [4/4] Final verification...
echo [SUCCESS] All cleanup operations completed

echo.
echo ========================================
echo [SUCCESS] Complete System Cleanup Done!
echo ========================================
echo.
echo Next steps:
echo   1. Start your bot (option 1)
echo   2. Wait 30 seconds for commands to sync
echo   3. Test commands in Discord
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

:droplet_restart
echo.
echo ========================================
echo Restart Droplet Bot
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
echo Restarting bot on droplet...
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 restart malabot"
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot restarted successfully
    ssh %DROPLET_USER%@%DROPLET_IP% "pm2 list"
) else (
    echo [ERROR] Failed to restart bot
)
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

REM Internal helper functions
:stop_internal
taskkill /FI "WINDOWTITLE eq MalaBoT Console" /F 2>NUL
tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "bot.py" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=2 delims=," %%P in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "bot.py"') do (
        taskkill /PID %%P /F 2>NUL
    )
)
goto :eof

:start_internal
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
if not exist "data" mkdir "data"
if not exist "data\logs" mkdir "data\logs"
start "MalaBoT Console" cmd /k "title MalaBoT Console && python bot.py"
goto :eof

:status_basic
tasklist /V /FI "WINDOWTITLE eq MalaBoT Console" 2>nul | find /I "MalaBoT Console" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Bot is RUNNING
) else (
    tasklist /FI "IMAGENAME eq python.exe" /FO CSV | findstr /I "bot.py" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [STATUS] Bot is RUNNING
    ) else (
        echo [STATUS] Bot is NOT RUNNING
    )
)
goto :eof

:get_current_branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set "current_branch=%%i"
goto :eof

:sync_db_from_droplet
echo.
echo ========================================
echo Sync Database from Droplet
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
set DROPLET_DIR=/home/malabot/MalaBoT
echo.
echo [WARNING] This will overwrite your local database!
echo [INFO] Your current local database will be backed up first.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo [CANCELLED] Database sync cancelled.
    pause
    goto menu
)

echo [1/3] Backing up current local database...
if exist bot.db (
    for /f "tokens=2 delims==." %%A in ('wmic os get localdatetime /value 2^>nul') do set "dt=%%A"
    set "TS=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%"
    if not exist "backups\db" mkdir "backups\db"
    copy /Y bot.db "backups\db\bot_local_%TS%.db" >nul
    echo [SUCCESS] Local database backed up to backups\db\bot_local_%TS%.db
)

echo [2/3] Downloading database from droplet...
scp %DROPLET_USER%@%DROPLET_IP%:%DROPLET_DIR%/data/bot.db data\bot.db

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to download database from droplet!
    pause
    goto menu
)

echo [3/3] Verifying database...
python -c "import sqlite3; conn = sqlite3.connect('data/bot.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM settings'); print('[SUCCESS] Database synced! Total settings:', cursor.fetchone()[0]); conn.close()"


echo.
echo ========================================
echo [SUCCESS] Database Sync Complete!
echo ========================================
echo Your local database now matches production.
echo.
pause
goto menu

:sync_db_to_droplet
echo.
echo ========================================
echo Sync Database TO Droplet
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
set DROPLET_DIR=/home/malabot/MalaBoT
echo.
echo [WARNING] This will overwrite the production database!
echo [INFO] The droplet's current database will be backed up first.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo [CANCELLED] Database sync cancelled.
    pause
    goto menu
)

echo [1/3] Backing up droplet database...
ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && mkdir -p backups/db && cp bot.db backups/db/bot_backup_$(date +%%Y-%%m-%%d_%%H-%%M-%%S).db"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to backup droplet database!
    pause
    goto menu
)

echo [2/3] Uploading local database to droplet...
scp data\bot.db %DROPLET_USER%@%DROPLET_IP%:%DROPLET_DIR%/data/bot.db


if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to upload database to droplet!
    pause
    goto menu
)

echo [3/3] Restarting bot on droplet...
ssh %DROPLET_USER%@%DROPLET_IP% "pm2 restart malabot"

echo.
echo ========================================
echo [SUCCESS] Database Synced to Droplet!
echo ========================================
echo Production database now matches your local database.
echo.
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
echo   5. Sync database to droplet
echo   6. Restart bot on droplet
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

echo [1/7] Staging all changes...
git add .

echo [2/7] Enter commit message:
set /p message="Commit message: "
if "%message%"=="" (
    echo [ERROR] Commit message cannot be empty!
    pause
    goto menu
)

echo [3/7] Committing changes...
git commit -m "%message%"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] No changes to commit or commit failed
)

echo [4/7] Pushing to GitHub branch: %current_branch%...
git push origin %current_branch%
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to push to GitHub!
    pause
    goto menu
)

echo [5/7] Deploying to droplet...
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
set DROPLET_DIR=/home/malabot/MalaBoT

ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && git fetch origin && git checkout %current_branch% && git reset --hard origin/%current_branch%"

echo [6/7] Syncing database to droplet...
scp data\bot.db %DROPLET_USER%@%DROPLET_IP%:%DROPLET_DIR%/data/bot.db


echo [7/7] Restarting bot on droplet...
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

:exit
echo.
echo [INFO] Thank you for using MalaBoT Development Tools!
echo.
pause
exit /b 0