@echo off
REM Simple Development Script for MalaBoT
REM Core functionality: Start, Stop, Restart, Update

setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

:menu
cls
echo ========================================
echo       MalaBoT Development Tools
echo ========================================
echo.
echo 1. Start Bot
echo 2. Stop Bot  
echo 3. Restart Bot
echo 4. Update Bot (Pull + Restart)
echo 5. Push Changes to GitHub
echo 6. Quick Deploy (Commit + Push)
echo.
echo 0. Exit
echo.
echo ========================================
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto update
if "%choice%"=="5" goto push
if "%choice%"=="6" goto deploy
if "%choice%"=="0" goto exit

echo Invalid choice. Try again.
timeout /T 2 >NUL
goto menu

:start
echo.
echo [INFO] Starting MalaBoT...
if not exist .env (
    echo [WARNING] .env file not found!
    if exist .env.example (
        copy .env.example .env >NUL
        echo [INFO] Created .env from template - please edit with your bot token!
        pause
        goto menu
    ) else (
        echo [ERROR] No .env file found!
        pause
        goto menu
    )
)

REM Clear cache
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d /r %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL

start "MalaBoT" cmd /k "python bot.py"
echo [SUCCESS] Bot started!
timeout /T 3 >NUL
goto menu

:stop
echo.
echo [INFO] Stopping MalaBoT...
taskkill /FI "WINDOWTITLE eq MalaBoT*" /F 2>NUL
taskkill /IM python.exe /F 2>NUL
echo [SUCCESS] Bot stopped!
timeout /T 2 >NUL
goto menu

:restart
echo.
echo [INFO] Restarting MalaBoT...
call :stop
timeout /T 2 >NUL
call :start
goto menu

:update
echo.
echo [1/3] Pulling latest changes from GitHub...
git pull origin main
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to pull from GitHub!
    pause
    goto menu
)

echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo [3/3] Restarting bot...
call :stop
timeout /T 2 >NUL
call :start

echo [SUCCESS] Bot updated and restarted!
goto menu

:push
echo.
echo [INFO] Pushing changes to GitHub...
git add .
git commit -m "Development update"
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Changes pushed to GitHub!
) else (
    echo [ERROR] Failed to push - check if you have changes to commit
)
timeout /T 3 >NUL
goto menu

:deploy
echo.
echo [INFO] Quick Deploy - Commit and Push...
set /p message="Enter commit message: "
if "%message%"=="" set message="Development update"

git add .
git commit -m "%message%"
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Changes deployed to GitHub!
) else (
    echo [ERROR] Deploy failed - check for uncommitted changes
)
timeout /T 3 >NUL
goto menu

:exit
exit /b 0