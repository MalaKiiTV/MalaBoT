@echo off
REM Professional Development Script for MalaBoT
REM This script handles the complete local development workflow

setlocal enabledelayedexpansion

:menu
cls
echo ========================================
echo    MalaBoT Professional Dev Tools
echo ========================================
echo.
echo LOCAL DEVELOPMENT:
echo 1. Start Bot (with cache clear)
echo 2. Stop Bot
echo 3. Restart Bot (with cache clear)
echo 4. View Live Logs
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
echo MAINTENANCE:
echo 12. Backup Database
echo 13. Clean Old Logs
echo 14. Check Bot Status
echo.
echo COMPLETE WORKFLOWS:
echo 15. Test Workflow (Stop → Clear Cache → Start → Logs)
echo 16. Deploy Workflow (Stage → Commit → Push)
echo.
echo 0. Exit
echo.
echo ========================================
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto clearcache
if "%choice%"=="6" goto gitstatus
if "%choice%"=="7" goto gitstage
if "%choice%"=="8" goto gitcommit
if "%choice%"=="9" goto gitpush
if "%choice%"=="10" goto gitpull
if "%choice%"=="11" goto githistory
if "%choice%"=="12" goto backup
if "%choice%"=="13" goto cleanlogs
if "%choice%"=="14" goto status
if "%choice%"=="15" goto testworkflow
if "%choice%"=="16" goto deployworkflow
if "%choice%"=="0" goto exit

echo Invalid choice. Please try again.
timeout /T 2 /NOBREAK >NUL
goto menu

:start
echo.
echo [1/3] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
echo [2/3] Starting MalaBoT...
start "MalaBoT" python bot.py
echo [3/3] Bot started successfully!
timeout /T 3 /NOBREAK >NUL
goto menu

:stop
echo.
echo [INFO] Stopping MalaBoT...
taskkill /FI "IMAGENAME eq python.exe" /F 2>NUL
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot stopped
) else (
    echo [INFO] No bot process found
)
timeout /T 2 /NOBREAK >NUL
goto menu

:restart
echo.
echo [1/4] Stopping bot...
taskkill /FI "IMAGENAME eq python.exe" /F 2>NUL
timeout /T 2 /NOBREAK >NUL
echo [2/4] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
echo [3/4] Starting bot...
start "MalaBoT" python bot.py
echo [4/4] Bot restarted successfully!
timeout /T 3 /NOBREAK >NUL
goto menu

:logs
echo.
echo [INFO] Opening live log viewer...
echo [INFO] Press Ctrl+C to stop viewing logs
echo.
timeout /T 2 /NOBREAK >NUL
powershell -Command "Get-Content -Path 'data\logs\bot.log' -Wait -Tail 50"
goto menu

:clearcache
echo.
echo [INFO] Clearing all caches...
echo [1/3] Clearing Python cache...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
echo [2/3] Clearing pytest cache...
rmdir /S /Q .pytest_cache 2>NUL
echo [3/3] Clearing command cache...
del /F /Q data\command_cache* 2>NUL
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
echo [SUCCESS] Changes committed!
timeout /T 2 /NOBREAK >NUL
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

:backup
echo.
echo [INFO] Creating database backup...
if not exist backups mkdir backups
for /f "tokens=2 delims==" %%I in ('wmic os get LocalDateTime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%
copy data\bot.db backups\bot_backup_%TIMESTAMP%.db >NUL
echo [SUCCESS] Database backed up to: backups\bot_backup_%TIMESTAMP%.db
timeout /T 3 /NOBREAK >NUL
goto menu

:cleanlogs
echo.
echo [INFO] Cleaning old logs (keeping last 10)...
for /f "skip=10 delims=" %%F in ('dir /B /O-D data\logs\*.log 2^>NUL') do (
    del "data\logs\%%F" 2>NUL
)
echo [SUCCESS] Old logs cleaned!
timeout /T 2 /NOBREAK >NUL
goto menu

:status
echo.
echo ========================================
echo Bot Status:
echo ========================================
tasklist /FI "IMAGENAME eq python.exe" | find "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [STATUS] Bot is RUNNING
    echo.
    tasklist /FI "IMAGENAME eq python.exe"
) else (
    echo [STATUS] Bot is NOT RUNNING
)
echo.
echo ========================================
pause
goto menu

:testworkflow
echo.
echo ========================================
echo Starting Test Workflow
echo ========================================
echo.
echo [1/5] Stopping bot...
taskkill /FI "IMAGENAME eq python.exe" /F 2>NUL
timeout /T 2 /NOBREAK >NUL

echo [2/5] Clearing caches...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

echo [3/5] Starting bot...
start "MalaBoT" python bot.py
timeout /T 5 /NOBREAK >NUL

echo [4/5] Checking status...
tasklist /FI "IMAGENAME eq python.exe" | find "python.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Bot is running!
) else (
    echo [ERROR] Bot failed to start!
)

echo [5/5] Opening logs...
timeout /T 2 /NOBREAK >NUL
powershell -Command "Get-Content -Path 'data\logs\bot.log' -Wait -Tail 50"
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

echo [5/5] Pushing to GitHub...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Deploy Workflow Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. SSH into your droplet
    echo 2. Run: ./update_droplet.sh
    echo.
) else (
    echo [ERROR] Failed to push to GitHub
)

pause
goto menu

:exit
echo.
echo [INFO] Exiting...
exit /b 0