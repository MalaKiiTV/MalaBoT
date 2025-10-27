@echo off
REM MalaBoT Diagnostic Tool
REM This script diagnoses and fixes common bot startup issues

setlocal enabledelayedexpansion

title MalaBoT Diagnostic Tool

echo ========================================
echo        MalaBoT Diagnostic Tool
echo ========================================
echo.

REM Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo [SUCCESS] Python %%i found
)

REM Check dependencies
echo [2/8] Checking required dependencies...
pip show discord.py >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] discord.py not found, installing...
    pip install discord.py
) else (
    for /f "tokens=2" %%i in ('pip show discord.py ^| findstr Version') do echo [SUCCESS] discord.py %%i found
)

pip show python-dotenv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] python-dotenv not found, installing...
    pip install python-dotenv
) else (
    for /f "tokens=2" %%i in ('pip show python-dotenv ^| findstr Version') do echo [SUCCESS] python-dotenv %%i found
)

REM Check file structure
echo [3/8] Checking file structure...
if not exist bot.py (
    echo [ERROR] bot.py not found!
    pause
    exit /b 1
) else (
    echo [SUCCESS] bot.py found
)

if not exist config\settings.py (
    echo [ERROR] config\settings.py not found!
    pause
    exit /b 1
) else (
    echo [SUCCESS] config\settings.py found
)

REM Create required directories
echo [4/8] Creating required directories...
if not exist data mkdir data
if not exist data\logs mkdir data\logs
if not exist backups mkdir backups
echo [SUCCESS] Directories created/verified

REM Check .env file
echo [5/8] Checking .env file...
if not exist .env (
    echo [WARNING] .env file not found!
    echo Creating .env file from template...
    if exist .env.example (
        copy .env.example .env >nul 2>&1
        echo [SUCCESS] .env file created from .env.example
        echo [IMPORTANT] Please edit .env and add your DISCORD_TOKEN and OWNER_IDS
    ) else (
        echo [ERROR] .env.example not found! Creating basic .env...
        (
            echo # Discord Bot Configuration
            echo DISCORD_TOKEN=your_bot_token_here
            echo BOT_PREFIX=/
            echo BOT_NAME=MalaBoT
            echo OWNER_IDS=your_discord_user_id_here
            echo LOG_LEVEL=INFO
            echo LOG_FILE=data/logs/bot.log
        ) > .env
        echo [SUCCESS] Basic .env file created
    )
) else (
    echo [SUCCESS] .env file found
)

REM Test configuration
echo [6/8] Testing configuration...
python -c "
import sys
try:
    from config.settings import settings
    errors = settings.validate()
    if errors:
        print('[ERROR] Configuration errors:')
        for error in errors:
            print(f'  - {error}')
        sys.exit(1)
    else:
        print('[SUCCESS] Configuration is valid!')
except Exception as e:
    print(f'[ERROR] Failed to load configuration: {e}')
    sys.exit(1)
" 2>NUL

if %ERRORLEVEL% NEQ 0 (
    echo [CRITICAL] Configuration test failed!
    echo.
    echo Please fix these issues:
    echo 1. Edit .env file
    echo 2. Add your DISCORD_TOKEN (from Discord Developer Portal)
    echo 3. Add your Discord User ID to OWNER_IDS
    echo 4. Save the file and run this diagnostic again
    echo.
    pause
    exit /b 1
)

REM Test import
echo [7/8] Testing bot imports...
python -c "
import sys
try:
    import discord
    import config.settings
    import utils.logger
    print('[SUCCESS] All imports successful!')
except ImportError as e:
    print(f'[ERROR] Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'[ERROR] Unexpected error: {e}')
    sys.exit(1)
" 2>NUL

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Import test failed!
    pause
    exit /b 1
)

REM Test bot startup (dry run)
echo [8/8] Testing bot startup...
python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from config.settings import settings
    print('Configuration loaded successfully')
    print(f'Discord Token: {&quot;SET&quot; if settings.DISCORD_TOKEN else &quot;NOT SET&quot;}')
    print(f'Owner IDs: {settings.OWNER_IDS if settings.OWNER_IDS else &quot;NOT SET&quot;}')
    print(f'Bot Prefix: {settings.BOT_PREFIX}')
    print('[SUCCESS] Bot startup test passed!')
except Exception as e:
    print(f'[ERROR] Startup test failed: {e}')
    sys.exit(1)
" 2>NUL

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Startup test failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo         DIAGNOSTIC COMPLETE
echo ========================================
echo.
echo [SUCCESS] All tests passed! Your bot should start correctly.
echo.
echo Next steps:
echo 1. Run dev.bat
echo 2. Choose option 1 to start the bot
echo 3. Use option 5 to view live logs if needed
echo.
echo If your bot still doesn't start:
echo - Check that your DISCORD_TOKEN is correct
echo - Verify your bot has proper permissions in Discord
echo - Use option 17 in dev.bat to test configuration
echo.

pause