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
echo ========================================
echo          MalaBoT Development Tools
echo ========================================
echo.
echo [BOT MANAGEMENT]
echo  1. Start Bot with cache clear
echo  2. Stop Bot
echo  3. Restart Bot with cache clear
echo  4. Check Bot Status
echo  5. View Live Logs
echo  6. Clear All Caches
echo.
echo [WORKFLOWS]
echo  7. Update Workflow
echo  8. Deploy Workflow
echo.
echo [GIT OPERATIONS]
echo  9.  Check Git Status
echo 10. Stage All Changes
echo 11. Commit Changes
echo 12. Push to GitHub
echo 13. Remote Deploy to Droplet
echo 14. Pull from GitHub
echo 15. View Commit History
echo.
echo [UTILITIES]
echo 16. Install Dependencies
echo 17. Create .env File
echo 18. Test Configuration
echo.
echo [ADVANCED OPS]
echo 19. Full Clean Update
echo 20. Backup Now
echo 21. Verify Environment
echo 22. Clear All (Commands + Caches + Logs + Temp)
echo 23. Fix /verify Command Structure
echo.
echo [EXIT]
echo  0. Exit
echo.
echo ========================================
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
if "%choice%"=="16" goto installdeps
if "%choice%"=="17" goto createenv
if "%choice%"=="18" goto testconfig
if "%choice%"=="19" goto fullupdate
if "%choice%"=="20" goto backupnow
if "%choice%"=="21" goto verifyenv
if "%choice%"=="22" goto clearall
if "%choice%"=="23" goto fixverify
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
REM First try to pull any remote changes
git pull origin main --rebase --no-edit >nul 2>&1
REM Then push using token authentication
git push https://x-access-token:%GITHUB_TOKEN%@github.com/MalaKiiTV/MalaBoT.git main
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pushed to GitHub successfully!
) else (
    echo [ERROR] Failed to push to GitHub
    echo [INFO] Make sure you have committed changes first
    echo [INFO] If GITHUB_TOKEN is not set, use: set GITHUB_TOKEN=your_token_here
)
timeout /T 3 /NOBREAK >NUL
goto menu

:gitpull
echo.
echo [INFO] Pulling from GitHub...
git pull origin main --no-edit
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pulled from GitHub successfully!
) else (
    echo [ERROR] Failed to pull from GitHub
)
timeout /T 3 /NOBREAK >NUL
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

echo [1/5] Pulling latest changes...
git pull origin main --no-edit
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

echo [5/5] Pushing to GitHub...
git push origin main

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
pip install -r requirements.txt
goto :eof

:createenv
echo.
if exist .env (
    echo [WARNING] .env file already exists!
    set /p overwrite="Do you want to overwrite it? (Y/N): "
    if /i not "%overwrite%"=="Y" goto menu
)

if exist .env.example (
    copy .env.example .env
    echo [SUCCESS] .env file created from template!
    echo.
    echo [IMPORTANT] Please edit .env file with your bot token and settings:
    echo - DISCORD_TOKEN: Your Discord bot token
    echo - OWNER_IDS: Your Discord user ID
    echo - BOT_PREFIX: Command prefix (default: /)
    echo.
    echo Open .env file and add your credentials before starting the bot.
) else (
    echo [ERROR] .env.example file not found!
    echo [INFO] Creating basic .env file template...
    (
        echo # Discord Bot Configuration
        echo DISCORD_TOKEN=your_bot_token_here
        echo BOT_PREFIX=/
        echo BOT_NAME=MalaBoT
        echo BOT_VERSION=1.0.0
        echo OWNER_IDS=your_discord_user_id_here
        echo.
        echo # Bot Settings
        echo LOG_LEVEL=INFO
        echo LOG_FILE=data/logs/bot.log
        echo.
        echo # Feature Flags
        echo ENABLE_MODERATION=true
        echo ENABLE_FUN=true
        echo ENABLE_UTILITY=true
    ) > .env
    echo [SUCCESS] Basic .env file created!
    echo [IMPORTANT] Please edit and add your bot token and user ID!
)
pause
goto menu

:testconfig
echo.
echo [INFO] Testing bot configuration...
if not exist .env (
    echo [ERROR] .env file not found! Use option 16 to create it.
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

:fullupdate
echo.
echo ========================================
echo Full Local Clean Update
echo ========================================
echo [1/6] Stopping bot...
call :stop_internal
echo [2/6] Backing up logs and DB...
call :backupnow
echo [3/6] Git reset/pull...
git reset --hard
git pull origin main --no-edit
echo [4/6] Installing dependencies...
call :installdeps_silent
echo [5/6] Clearing caches...
call :clearcache
echo [6/6] Restarting bot...
call :start_internal
timeout /T 3 /NOBREAK >NUL
call :status_basic
echo [SUCCESS] Full update complete!
pause
goto menu

:remotedeploy
echo.
echo ========================================
echo Remote Deploy to Droplet
echo ========================================
set DROPLET_USER=malabot
set DROPLET_IP=165.232.156.230
set DROPLET_DIR=/home/malabot/MalaBoT
echo [1/4] Pushing local changes to GitHub...
REM First pull any remote changes
git pull origin main --rebase --no-edit >nul 2>&1
REM Then push using token authentication
git push https://x-access-token:%GITHUB_TOKEN%@github.com/MalaKiiTV/MalaBoT.git main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git push failed. Commit first or set GITHUB_TOKEN.
    pause
    goto menu
)
echo [2/4] SSH into droplet and update...
ssh %DROPLET_USER%@%DROPLET_IP% "cd %DROPLET_DIR% && git reset --hard && git pull origin main"
echo [3/4] Restart bot remotely...
ssh %DROPLET_USER%@%DROPLET_IP% "pkill -f bot.py || true; nohup python3 bot.py > data/logs/latest.log 2>&1 &"
echo [4/4] Checking latest remote logs...
ssh %DROPLET_USER%@%DROPLET_IP% "tail -n 20 %DROPLET_DIR%/data/logs/latest.log"
echo [DONE] Remote deploy complete.
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
if exist "data\logs" xcopy "data\logs" "backups\logs\%TS%&quot; /E /Q /Y >nul
if exist "data\bot.db" copy /Y "data\bot.db" "backups\db\bot_%TS%.db" >nul
echo [SUCCESS] Backup saved with tag %TS%.
goto :eof

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

:fixverify
echo.
echo ========================================
echo Fix /verify Command Structure
echo ========================================
echo.
echo This will fix the /verify command to show as a parent
echo command with subcommands (submit, review, setup) instead
echo of separate individual commands.
echo.
set /p confirm="Continue? (yes/no): "
if /i "%confirm%"=="yes" goto fixverify_continue
if /i "%confirm%"=="y" goto fixverify_continue
echo [CANCELLED] Operation cancelled.
timeout /T 2 /NOBREAK >NUL
goto menu

:fixverify_continue
echo.
echo [1/2] Stopping bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL

echo [2/2] Running verify command fix...
python fix_verify_command.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Fix script failed
    pause
    goto menu
)

echo.
echo ========================================
echo [SUCCESS] /verify Command Structure Fixed!
echo ========================================
echo.
echo Next steps:
echo   1. Start your bot (option 1)
echo   2. Wait 30 seconds
echo   3. In Discord, type /verify and press space
echo   4. You should see: submit, review, setup
echo   5. If not, restart Discord (Ctrl+R)
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

:exit
echo.
echo [INFO] Thank you for using MalaBoT Development Tools!
echo.
pause
exit /b 0