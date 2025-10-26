@echo off
REM Fixed Development Script for MalaBoT
REM This script handles the complete local development workflow

setlocal enabledelayedexpansion

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
echo 5. Clear All Caches
echo.
echo GIT OPERATIONS:
echo 6. Check Git Status
echo 7. Stage All Changes
echo 8. Commit Changes
echo 9. Push to GitHub
echo 10. Pull from GitHub
echo 11. View Commit History
echo.
echo COMPLETE WORKFLOWS:
echo 12. Update Workflow (Pull -> Restart -> Status)
echo 13. Deploy Workflow (Stage -> Commit -> Push)
echo.
echo UTILITIES:
echo 14. Install/Update Dependencies
echo 15. Create .env file from template
echo.
echo 0. Exit
echo.
echo ========================================
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto clearcache
if "%choice%"=="6" goto gitstatus
if "%choice%"=="7" goto gitstage
if "%choice%"=="8" goto gitcommit
if "%choice%"=="9" goto gitpush
if "%choice%"=="10" goto gitpull
if "%choice%"=="11" goto githistory
if "%choice%"=="12" goto updateworkflow
if "%choice%"=="13" goto deployworkflow
if "%choice%"=="14" goto installdeps
if "%choice%"=="15" goto createenv
if "%choice%"=="0" goto exit

echo Invalid choice. Please try again.
timeout /T 2 /NOBREAK >NUL
goto menu

:start
echo.
echo [1/3] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [2/3] Checking for .env file...
if not exist .env (
    echo [WARNING] .env file not found!
    echo [INFO] Creating from template...
    if exist .env.example (
        copy .env.example .env >NUL
        echo [INFO] Please edit .env file with your bot token and settings
        pause
    ) else (
        echo [ERROR] .env.example file not found!
        pause
        goto menu
    )
)

echo [3/3] Starting MalaBoT...
start "MalaBoT - Discord Bot" cmd /k "python bot.py"
echo [SUCCESS] Bot started in new window!
timeout /T 3 /NOBREAK >NUL
goto menu

:stop
echo.
echo [INFO] Stopping MalaBoT...
REM Kill specific bot processes by window title
taskkill /FI "WINDOWTITLE eq MalaBoT - Discord Bot*" /F 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot stopped
) else (
    REM Fallback: Kill python processes running bot.py
    wmic process where "name='python.exe' and commandline like '%bot.py%'" delete 2>NUL
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Bot stopped (fallback method)
    ) else (
        echo [INFO] No bot process found
    )
)
timeout /T 2 /NOBREAK >NUL
goto menu

:restart
echo.
echo [1/4] Stopping bot...
taskkill /FI "WINDOWTITLE eq MalaBoT - Discord Bot*" /F 2>NUL
wmic process where "name='python.exe' and commandline like '%bot.py%'" delete 2>NUL
timeout /T 2 /NOBREAK >NUL

echo [2/4] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [3/4] Starting bot...
start "MalaBoT - Discord Bot" cmd /k "python bot.py"

echo [4/4] Bot restarted successfully!
timeout /T 3 /NOBREAK >NUL
goto menu

:status
echo.
echo ========================================
echo Bot Status:
echo ========================================
tasklist /FI "WINDOWTITLE eq MalaBoT - Discord Bot*" | find "cmd.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Bot is RUNNING
    echo.
    echo Running processes:
    tasklist /FI "WINDOWTITLE eq MalaBoT - Discord Bot*"
) else (
    wmic process where "name='python.exe' and commandline like '%bot.py%'" get processid,name,commandline 2>NUL | find "bot.py" >NUL
    if %ERRORLEVEL% EQU 0 (
        echo [STATUS] Bot is RUNNING (process detected)
        echo.
        wmic process where "name='python.exe' and commandline like '%bot.py%'" get processid,name,commandline
    ) else (
        echo [STATUS] Bot is NOT RUNNING
    )
)
echo.
echo ========================================
pause
goto menu

:clearcache
echo.
echo [INFO] Clearing all caches...
echo [1/3] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [2/3] Clearing pytest cache...
rmdir /S /Q .pytest_cache 2>NUL

echo [3/3] Cleaning temporary files...
del /F /Q *.tmp 2>NUL
del /F /Q *.log 2>NUL

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

echo [1/4] Pulling latest changes...
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull from GitHub!
    pause
    goto menu
)

echo [2/4] Installing/Updating dependencies...
pip install -r requirements.txt

echo [3/4] Restarting bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL
call :start_internal

echo [4/4] Checking status...
timeout /T 3 /NOBREAK >NUL
call :status_internal

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
    echo - DISCORD_BOT_TOKEN: Your Discord bot token
    echo - Other required configuration values
    echo.
    echo Open .env file and add your credentials before starting the bot.
) else (
    echo [ERROR] .env.example file not found!
    echo [INFO] Creating basic .env file template...
    (
        echo # Discord Bot Configuration
        echo DISCORD_BOT_TOKEN=your_bot_token_here
        echo.
        echo # Bot Settings
        echo BOT_PREFIX=!
        echo BOT_STATUS=online
        echo.
        echo # Add other configuration as needed
    ) > .env
    echo [SUCCESS] Basic .env file created!
    echo [IMPORTANT] Please edit and add your bot token!
)
pause
goto menu

REM Internal helper functions
:stop_internal
taskkill /FI "WINDOWTITLE eq MalaBoT - Discord Bot*" /F 2>NUL
wmic process where "name='python.exe' and commandline like '%bot.py%'" delete 2>NUL
goto :eof

:start_internal
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
start "MalaBoT - Discord Bot" cmd /k "python bot.py"
goto :eof

:status_internal
tasklist /FI "WINDOWTITLE eq MalaBoT - Discord Bot*" | find "cmd.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Bot is RUNNING
) else (
    wmic process where "name='python.exe' and commandline like '%bot.py%'" get processid,name,commandline 2>NUL | find "bot.py" >NUL
    if %ERRORLEVEL% EQU 0 (
        echo [STATUS] Bot is RUNNING
    ) else (
        echo [STATUS] Bot is NOT RUNNING
    )
)
goto :eof

:exit
echo.
echo [INFO] Exiting...
exit /b 0