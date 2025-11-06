@echo off
REM FIXED Development Script for MalaBoT
REM This script handles the complete local development workflow

setlocal enabledelayedexpansion
chcp 65001 >nul

REM Set window title
title MalaBoT Development Tools

REM Configure git to never open editor for merges and handle authentication
git config pull.rebase false >nul 2>&1
git config merge.commit no >nul 2>&1
git config core.editor "echo" >nul 2>&1
git config credential.helper store >nul 2>&1

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] This is not a Git repository!
    echo Please navigate to the MalaBoT directory first.
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
echo 13. Pull from GitHub             - Get latest changes from remote (MAIN BRANCH)
echo 14. Switch Branch                - Switch to different branch
echo 15. View Commit History          - Show last 10 commits
echo.
echo [UTILITIES]
echo 16. Install Dependencies         - Install/update Python packages
echo 17. Test Configuration           - Validate .env settings
echo 18. Create Backup                - Backup logs and database
echo 19. Environment Check            - Check configuration validity
echo.
echo [EXIT]
echo  0. Exit                         - Close development tools
echo.
echo ================================================================================
echo.

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
if "%choice%"=="13" goto gitpull_main
if "%choice%"=="14" goto switchbranch
if "%choice%"=="15" goto githistory
if "%choice%"=="16" goto installdeps
if "%choice%"=="17" goto testconfig
if "%choice%"=="18" goto backupnow
if "%choice%"=="19" goto verifyenv
if "%choice%"=="0" goto exit

echo Invalid choice. Please try again.
timeout /T 2 /NOBREAK >NUL
goto menu

:start
echo.
echo [INFO] Starting MalaBoT...
echo.

REM Clear cache
call :clearcache_internal

REM Validate configuration
echo [INFO] Validating configuration...
python -c "from config.settings import settings; errors = settings.validate(); print('Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Configuration validation failed. Please check your .env file.
    echo.
    echo [IMPORTANT] Please edit .env file with your bot token and settings:
    echo          - DISCORD_TOKEN: Your Discord bot token
    echo          - OWNER_IDS: Your Discord user ID
    echo.
    pause
    goto menu
)

REM Start bot
echo [INFO] Starting bot...
start "MalaBoT" cmd /k "python bot.py"
echo [SUCCESS] Bot started in new window!
timeout /T 2 /NOBREAK >NUL
goto menu

:stop
echo.
echo [INFO] Stopping MalaBoT...
call :stop_internal
goto menu

:stop_internal
REM Method 1: Try to close by window title
taskkill /FI "WINDOWTITLE eq MalaBoT*" /F >nul 2>&1

REM Method 2: Try to find and kill python processes running bot.py
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    wmic process where "ProcessId=%%i" get CommandLine /format:list 2>nul | find "bot.py" >nul
    if !ERRORLEVEL! EQU 0 (
        taskkill /PID %%i /F >nul 2>&1
    )
)

REM Method 3: Fallback - try all python processes (safer approach)
timeout /T 1 /NOBREAK >NUL
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Python processes still running. Please check manually.
) else (
    echo [SUCCESS] Bot stopped successfully!
)
goto :eof

:restart
echo.
echo [INFO] Restarting MalaBoT...
call :stop_internal
timeout /T 2 /NOBREAK >NUL
goto start

:status
echo.
echo Bot Status:
echo ==========
echo.

REM Check for running python processes
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [RUNNING] Bot process(es) detected:
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
    
    REM Check if bot.py is running
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
        wmic process where "ProcessId=%%i" get CommandLine /format:list 2>nul | find "bot.py" >nul
        if !ERRORLEVEL! EQU 0 (
            echo [CONFIRMED] bot.py is running (PID: %%i)
        )
    )
) else (
    echo [STOPPED] No bot processes detected.
)

echo.
if exist "bot.db" (
    for %%F in ("bot.db") do (
        set "ts_raw=%%~tF"
        set "ts=!ts_raw:~0,4!-!ts_raw:~4,2!-!ts_raw:~6,2! !ts_raw:~8,2!:!ts_raw:~10,2!"
    )
    echo Database: bot.db (Modified: !ts!)
) else (
    echo Database: bot.db (NOT FOUND)
)

if exist "data\logs\bot.log" (
    for %%F in ("data\logs\bot.log") do (
        set "ts_raw=%%~tF"
        set "ts=!ts_raw:~0,4!-!ts_raw:~4,2!-!ts_raw:~6,2! !ts_raw:~8,2!:!ts_raw:~10,2!"
    )
    echo Log File: data\logs\bot.log (Modified: !ts!)
) else (
    echo Log File: data\logs\bot.log (NOT FOUND)
)

echo.
echo Recent log entries (last 10 lines):
if exist "data\logs\bot.log" (
    powershell "Get-Content 'data\logs\bot.log' -Tail 10"
) else (
    echo [WARNING] Log file not found at: data\logs\bot.log
)

echo.
pause
goto menu

:logs
echo.
echo [INFO] Viewing live logs (Press Ctrl+C to stop)...
echo.
if exist "data\logs\bot.log" (
    powershell "Get-Content 'data\logs\bot.log' -Wait -Tail 20"
) else (
    echo [ERROR] Log file not found: data\logs\bot.log
    pause
)
goto menu

:clearcache
echo.
echo [INFO] Clearing all caches...
call :clearcache_internal
echo [SUCCESS] All caches cleared!
timeout /T 2 /NOBREAK >NUL
goto menu

:clearcache_internal
REM Clear Python cache
if exist "__pycache__" rmdir /s /q "__pycache__" >nul 2>&1
if exist ".pytest_cache" rmdir /s /q ".pytest_cache" >nul 2>&1
if exist "data\logs\*.log" del /q "data\logs\*.log" >nul 2>&1
if exist "*.pyc" del /q "*.pyc" >nul 2>&1

REM Clear temp files
if exist "temp" rmdir /s /q "temp" >nul 2>&1
if exist "tmp" rmdir /s /q "tmp" >nul 2>&1

REM Clear Python bytecode cache recursively
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
goto :eof

:updateworkflow
echo.
echo [INFO] Starting Update Workflow...
echo [1/5] Pulling latest changes from main branch...

REM Switch to main branch first
git checkout main >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to switch to main branch!
    pause
    goto menu
)

git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull from GitHub!
    pause
    goto menu
)

echo [2/5] Installing dependencies...
call :installdeps_internal

echo [3/5] Clearing caches...
call :clearcache_internal

echo [4/5] Restarting bot...
call :stop_internal
timeout /T 2 /NOBREAK >NUL

echo [5/5] Starting bot...
call :start_internal

echo [SUCCESS] Update workflow completed!
timeout /T 3 /NOBREAK >NUL
goto menu

:start_internal
python -c "from config.settings import settings; errors = settings.validate(); print('Configuration OK' if not errors else f'Errors: {errors}')" 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Configuration validation failed.
    pause
    goto :eof
)

start "MalaBoT" cmd /k "python bot.py"
goto :eof

:deployworkflow
echo.
echo [INFO] Starting Deploy Workflow...
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

echo [1/5] Checking git status...
git status --short
echo.

echo [2/5] Staging all changes...
git add -A
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to stage changes!
    pause
    goto menu
)

echo [3/5] Committing changes...
set /p commit_msg="Enter commit message: "
if "%commit_msg%"=="" (
    echo [ERROR] Commit message cannot be empty!
    pause
    goto menu
)

git commit -m "%commit_msg%"
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Nothing to commit or commit failed.
) else (
    echo [SUCCESS] Changes committed!
)

echo [4/5] Pushing to GitHub...
git push origin %current_branch%
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Pushed to GitHub successfully!
) else (
    echo [ERROR] Failed to push to GitHub. Check your connection and permissions.
    pause
    goto menu
)

echo [5/5] Deployment workflow completed!
echo.
timeout /T 3 /NOBREAK >NUL
goto menu

:gitstatus
echo.
echo Git Status:
echo ==========
git status
echo.
pause
goto menu

:gitstage
echo.
echo Staging files...
git add -A
echo Staged files:
git status --short
echo.
pause
goto menu

:gitcommit
echo.
echo Committing staged changes...
set /p commit_msg="Enter commit message: "
if "%commit_msg%"=="" (
    echo [ERROR] Commit message cannot be empty!
    pause
    goto menu
)

git commit -m "%commit_msg%"
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Changes committed!
) else (
    echo [WARNING] Nothing to commit or commit failed.
)
echo.
pause
goto menu

:gitpush
echo.
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
    echo [ERROR] Failed to push to GitHub. Check your connection and permissions.
)
echo.
pause
goto menu

:gitpull_main
echo.
echo [INFO] Pulling from GitHub main branch...
echo [WARNING] This will switch to main branch and pull latest changes.
echo Any local changes will be stashed first.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo [CANCELLED] Pull cancelled.
    pause
    goto menu
)

REM Stash any local changes
git stash push -m "Auto-stash before pull" >nul 2>&1

REM Switch to main and pull
git checkout main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to switch to main branch!
    pause
    goto menu
)

git pull origin main
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Pulled latest changes from main branch!
    
    REM Check if we stashed anything
    git stash list >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] You had local changes that were stashed.
        set /p restore_stash="Restore stashed changes? (y/n): "
        if /i "%restore_stash%"=="y" (
            git stash pop
            echo [INFO] Stashed changes restored.
        )
    )
) else (
    echo.
    echo [ERROR] Failed to pull from GitHub. Your local changes might conflict.
    echo [INFO] Use 'git status' to see conflicting files.
)
echo.
pause
goto menu

:switchbranch
echo.
echo Available branches:
git branch -a
echo.
set /p branch_name="Enter branch name to switch to: "
if "%branch_name%"=="" (
    echo [ERROR] Branch name cannot be empty!
    pause
    goto menu
)

git checkout %branch_name%
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Switched to branch: %branch_branch%
) else (
    echo [ERROR] Failed to switch to branch: %branch_name%
    echo [INFO] Use 'git branch -r' to see available remote branches.
)
echo.
pause
goto menu

:githistory
echo.
echo Commit History (last 10):
echo ========================
git log --oneline -10
echo.
pause
goto menu

:installdeps
echo.
echo [INFO] Installing/updating dependencies...
call :installdeps_internal
echo [SUCCESS] Dependencies installed!
pause
goto menu

:installdeps_internal
pip install -r requirements.txt --upgrade
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some dependencies may have failed to install.
)
goto :eof

:testconfig
echo.
echo [INFO] Testing configuration...
python -c "from config.settings import settings; errors = settings.validate(); print(f'Configuration OK' if not errors else f'Errors: {errors}')"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Configuration validation failed!
    echo.
    echo [INFO] Please check your .env file and ensure:
    echo - DISCORD_TOKEN is set and valid
    echo - OWNER_IDS contains your Discord user ID(s)
    echo - Other required settings are properly configured
) else (
    echo [SUCCESS] Configuration is valid!
)
echo.
pause
goto menu

:backupnow
echo.
echo [INFO] Creating backup...
set "backup_dir=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%"
set "backup_dir=%backup_dir: =0%"

if not exist "%backup_dir%" mkdir "%backup_dir%"

REM Backup database
if exist "bot.db" copy "bot.db" "%backup_dir%&quot; >nul 2>&1

REM Backup logs
if exist "data\logs" xcopy "data\logs" "%backup_dir%\logs&quot; /E /I >nul 2>&1

REM Backup config
if exist ".env" copy ".env" "%backup_dir%&quot; >nul 2>&1

echo [SUCCESS] Backup created: %backup_dir%
pause
goto menu

:verifyenv
echo.
echo [INFO] Verifying environment...
echo.

REM Python version
python --version

REM Git status
echo Git repository: 
git rev-parse --git-dir >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Git repository detected
    call :get_current_branch
    echo Current branch: %current_branch%
) else (
    echo [ERROR] Not a Git repository!
)

REM Configuration check
python -c "from config.settings import settings; errors = settings.validate(); print('Configuration: VALID' if not errors else f'Configuration: INVALID ({len(errors)} errors)')" 2>NUL

REM Dependencies check
pip show discord.py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Dependencies: discord.py installed
) else (
    echo Dependencies: discord.py NOT installed
)

REM Files check
if exist "bot.py" (
    echo Files: bot.py found
) else (
    echo Files: bot.py NOT found
)

if exist "bot.db" (
    echo Database: bot.db found
) else (
    echo Database: bot.db not found (will be created on first run)
)

echo.
pause
goto menu

:get_current_branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "current_branch=%%i"
if not defined current_branch set "current_branch=unknown"
goto :eof

:exit
echo.
echo [INFO] Thank you for using MalaBoT Development Tools!
echo.
pause
exit /b 0