@echo off
REM COMPLETELY FIXED Development Script for MalaBoT
REM This script handles the complete local development workflow

setlocal enabledelayedexpansion
chcp 65001 >nul
reg add "HKCU\Console\%~n0" /v FaceName /t REG_SZ /d "Consolas" /f >nul 2>&1

REM Set window title
title MalaBoT Development Tools

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
echo    MalaBoT Professional Dev Tools
echo ========================================
echo.
echo BOT MANAGEMENT:
echo 1. Start Bot (with cache clear)
echo 2. Stop Bot
echo 3. Restart Bot (with cache clear)
echo 4. Check Bot Status
echo 5. View Live Logs
echo 6. Clear All Caches
echo.
echo GIT OPERATIONS:
echo 7. Check Git Status
echo 8. Stage All Changes
echo 9. Commit Changes
echo 10. Push to GitHub
echo 11. Pull from GitHub
echo 12. View Commit History
echo.
echo COMPLETE WORKFLOWS:
echo 13. Update Workflow (Pull -> Restart -> Status)
echo 14. Deploy Workflow (Stage -> Commit -> Push)
echo.
echo UTILITIES:
echo 15. Install/Update Dependencies
echo 16. Create .env file from template
echo 17. Test Bot Configuration
echo.
echo ADVANCED OPS:
echo 18. Full Local Clean Update
echo 19. Remote Deploy to Droplet
echo 20. Backup Now
echo 21. Verify Environment
echo.
echo 0. Exit
echo.
echo ========================================
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto clearcache
if "%choice%"=="7" goto gitstatus
if "%choice%"=="8" goto gitstage
if "%choice%"=="9" goto gitcommit
if "%choice%"=="10" goto gitpush
if "%choice%"=="11" goto gitpull
if "%choice%"=="12" goto githistory
if "%choice%"=="13" goto updateworkflow
if "%choice%"=="14" goto deployworkflow
if "%choice%"=="15" goto installdeps
if "%choice%"=="16" goto createenv
if "%choice%"=="17" goto testconfig
if "%choice%"=="0" goto exit
if "%choice%"=="18" goto fullupdate
if "%choice%"=="19" goto remotedeploy
if "%choice%"=="20" goto backupnow
if "%choice%"=="21" goto verifyenv

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
python -c "from config.settings import settings; errors = settings.validate(); print(f'Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
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
REM Try to close the bot window cleanly
taskkill /FI "WINDOWTITLE eq MalaBoT Console" /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot stopped via window title
) else (
    REM Fallback: Try both python.exe and python3.exe for safety
    wmic process where "name='python.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
    wmic process where "name='python3.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Bot stopped via process detection
    ) else (
        echo [WARNING] No running bot process found
    )
)
timeout /T 2 /NOBREAK >nul
goto menu


:restart
echo.
echo [1/5] Stopping bot...
taskkill /FI "WINDOWTITLE eq MalaBoT Console" /F >nul 2>&1
wmic process where "name='python.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
wmic process where "name='python3.exe' and commandline like '%%bot.py%%'" delete >nul 2>&1
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

python -c "from config.settings import settings; errors = settings.validate(); print(f'Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
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

REM Detect bot process by title or command line
set "bot_running=0"

for /f "tokens=1 delims=," %%A in ('tasklist /FI "IMAGENAME eq python.exe" /V /FO CSV ^| findstr /I "bot.py"') do set "bot_running=1"
for /f "tokens=1 delims=," %%A in ('tasklist /FI "IMAGENAME eq python3.exe" /V /FO CSV ^| findstr /I "bot.py"') do set "bot_running=1"

if "%bot_running%"=="1" (
    echo [STATUS] Bot is RUNNING
    echo.
    echo Running processes:
    tasklist /FI "IMAGENAME eq python.exe" /V /FO TABLE | findstr /I "bot.py"
    tasklist /FI "IMAGENAME eq python3.exe" /V /FO TABLE | findstr /I "bot.py"
) else (
    echo [STATUS] Bot is NOT RUNNING
)

echo.
echo ========================================
echo Recent log entries (last 10 lines):
echo ========================================

if exist "data\logs\bot.log" (
    echo [INFO] Displaying last 10 log lines...
    powershell -NoLogo -NoProfile -Command ^
        "Try {Get-Content 'data/logs/bot.log' -Tail 10 -Encoding UTF8 | ForEach-Object {$_ -replace '[^\x20-\x7E]',''} } Catch {Write-Host '[ERROR] Unable to read log file.'}"
) else (
    echo [INFO] No log file found - bot may not have started yet
)

echo ========================================
echo.
pause
goto menu

:logs
echo.
echo [INFO] Opening live log viewer...
echo [INFO] Press Ctrl+C to stop viewing logs
echo.

if exist "data\logs\bot.log" (
    powershell -Command "Get-Content 'data\logs\bot.log' -Wait -Tail 20"
) else (
    echo [WARNING] Log file not found at: data\logs\bot.log
    echo [INFO] Waiting for log file to be created...
    timeout /T 5 /NOBREAK >NUL
    if exist "data\logs\bot.log" (
        powershell -Command "Get-Content 'data\logs\bot.log' -Wait -Tail 20"
    ) else (
        echo [ERROR] Log file still not found - check if bot is running
    )
)
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
    for /f "skip=5 delims=" %%F in ('dir /B /O-D data\logs\*.log 2^>NUL') do (
        del "data\logs\%%F" 2>NUL
    )
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
git push origin main
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pushed to GitHub successfully!
) else (
    echo [ERROR] Failed to push to GitHub
    echo [INFO] Make sure you have committed changes first
    echo [INFO] Check your authentication with GitHub
)
timeout /T 3 /NOBREAK >NUL
goto menu

:gitpull
echo.
echo [INFO] Pulling from GitHub...
git pull origin main
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pulled from GitHub successfully!
) else (
    echo [ERROR] Failed to pull from GitHub
    echo [INFO] Check your internet connection and repository access
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
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull from GitHub!
    pause
    goto menu
)

echo [2/5] Installing/Updating dependencies...
pip install -r requirements.txt

echo [3/5] Restarting bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL
call :start_internal

echo [4/5] Checking status...
timeout /T 3 /NOBREAK >NUL
call :status_internal

echo [5/5] Opening logs...
timeout /T 2 /NOBREAK >NUL
call :logs_internal

echo.
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
echo [INFO] Installing/Updating dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Dependencies installed successfully!
) else (
    echo [ERROR] Failed to install dependencies!
)
timeout /T 3 /NOBREAK >NUL
goto menu

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
    echo - OWNER_IDS: Your Discord user ID (comma-separated if multiple)
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

python -c "
try:
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

REM Internal helper functions
:stop_internal
taskkill /FI "WINDOWTITLE eq MalaBoT Console" /F 2>NUL
wmic process where "name='python.exe' and commandline like '%bot.py%'" delete 2>NUL
goto :eof

:start_internal
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
if not exist "data" mkdir "data"
if not exist "data\logs" mkdir "data\logs"
start "MalaBoT Console" cmd /k "title MalaBoT Console && python bot.py"
goto :eof

:status_internal
set "bot_running=0"
tasklist /v /fo table | find /I "MalaBoT Console" >nul 2>&1 && set "bot_running=1"
if %bot_running%==0 (
    wmic process where "commandline like '%%bot.py%%'" get processid,name,commandline 2>nul | find /I "bot.py" >nul && set "bot_running=1"
)

if %bot_running%==1 (
    echo [STATUS] Bot is RUNNING
) else (
    echo [STATUS] Bot is NOT RUNNING
)
goto :eof


:logs_internal
if exist "data\logs\bot.log" (
    powershell -Command "Get-Content 'data\logs\bot.log' | Select-Object -Last 10"
) else (
    echo [INFO] No log file found
)
goto :eof

:exit
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
git pull origin main
echo [4/6] Installing/Updating dependencies...
call :installdeps
echo [5/6] Clearing caches...
call :clearcache
echo [6/6] Restarting bot...
call :start_internal
timeout /T 3 /NOBREAK >NUL
call :status_internal
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
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git push failed. Commit first.
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
set "TS=%date:~-4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%"
set "TS=%TS: =0%"
if not exist "backups\logs" mkdir "backups\logs"
if not exist "backups\db" mkdir "backups\db"
if exist "data\logs" xcopy "data\logs" "backups\logs\%TS%\" /E /Q /Y >nul
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
python - <<PY
from config.settings import settings
try:
    errs = settings.validate()
    if errs:
        print("[ERROR] Config validation failed:")
        [print(" -", e) for e in errs]
    else:
        print("[OK] Environment validated successfully.")
        print("BOT_NAME:", settings.BOT_NAME)
        print("BOT_PREFIX:", settings.BOT_PREFIX)
except Exception as e:
    print("[ERROR] Failed to verify environment:", e)
PY
pause
goto menu
