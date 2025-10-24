@echo off
REM MalaBoT Update Script for Windows
REM Fully clean, update, and restart MalaBoT

setlocal enabledelayedexpansion

REM Configuration
set BOT_DIR=%~dp0
set BACKUP_DIR=%BOT_DIR%backups
set LOG_DIR=%BOT_DIR%data\logs
set DB_FILE=%BOT_DIR%data\bot.db
set PYTHON_CMD=python
set RESTART_REASON=%1

if "%RESTART_REASON%"=="" set RESTART_REASON=manual

REM Colors (Windows 10+ ANSI support)
set RED=[91m
set GREEN=[92m
set YELLOW=[93m
set BLUE=[94m
set NC=[0m

REM Create timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get LocalDateTime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%-%datetime:~8,2%%datetime:~10,2%
set UPDATE_LOG=%LOG_DIR%\update_%TIMESTAMP%.log

echo %GREEN%[%date% %time%]%NC% Starting MalaBoT update process...
echo %GREEN%[%date% %time%]%NC% Restart reason: %RESTART_REASON%
echo %GREEN%[%date% %time%]%NC% Update log: %UPDATE_LOG%

REM Create directories
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%BACKUP_DIR%\logs\%TIMESTAMP%" mkdir "%BACKUP_DIR%\logs\%TIMESTAMP%"
if not exist "%BACKUP_DIR%\db\%TIMESTAMP%" mkdir "%BACKUP_DIR%\db\%TIMESTAMP%"
if not exist "%BOT_DIR%\data\flags" mkdir "%BOT_DIR%\data\flags"

REM Function to stop the bot
echo %GREEN%[%date% %time%]%NC% Stopping MalaBoT process...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq bot.py*" 2>NUL
timeout /T 3 /NOBREAK >NUL

REM Function to create backups
echo %GREEN%[%date% %time%]%NC% Creating backups...

REM Backup logs
if exist "%LOG_DIR%\*" (
    echo %GREEN%[%date% %time%]%NC% Backing up logs to %BACKUP_DIR%\logs\%TIMESTAMP%
    xcopy "%LOG_DIR%\*" "%BACKUP_DIR%\logs\%TIMESTAMP%&quot; /E /I /Y >NUL 2>&1
)

REM Backup database
if exist "%DB_FILE%" (
    echo %GREEN%[%date% %time%]%NC% Backing up database to %BACKUP_DIR%\db\%TIMESTAMP%
    copy "%DB_FILE%" "%BACKUP_DIR%\db\%TIMESTAMP%\bot.db" >NUL
)

REM Backup .env file
if exist "%BOT_DIR%.env" (
    copy "%BOT_DIR%.env" "%BACKUP_DIR%\env_backup_%TIMESTAMP%" >NUL
)

REM Function to update from Git
echo %GREEN%[%date% %time%]%NC% Updating code from Git...
cd /D "%BOT_DIR%"

git fetch --all
git reset --hard origin/main

for /f "delims=" %%I in ('git log -1 --oneline') do set LATEST_COMMIT=%%I
echo %GREEN%[%date% %time%]%NC% Updated to: %LATEST_COMMIT%

REM Function to update dependencies
echo %GREEN%[%date% %time%]%NC% Updating Python dependencies...

REM Check if virtual environment exists
if not exist "venv" (
    echo %GREEN%[%date% %time%]%NC% Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment and update dependencies
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade

REM Function to clean old backups
echo %GREEN%[%date% %time%]%NC% Cleaning old backups...

REM Clean old log backups (keep 10 most recent)
for /f "skip=10 delims=" %%D in ('dir /B /AD /O-N "%BACKUP_DIR%\logs" 2^>NUL') do (
    rmdir /S /Q "%BACKUP_DIR%\logs\%%D" 2>NUL
)

REM Clean old database backups (keep 10 most recent)
for /f "skip=10 delims=" %%D in ('dir /B /AD /O-N "%BACKUP_DIR%\db" 2^>NUL') do (
    rmdir /S /Q "%BACKUP_DIR%\db\%%D" 2>NUL
)

REM Clean old env backups (keep 5)
for /f "skip=5 delims=" %%F in ('dir /B /O-N "%BACKUP_DIR%\env_backup_*" 2^>NUL') do (
    del "%BACKUP_DIR%\%%F" 2>NUL
)

REM Function to clean caches
echo %GREEN%[%date% %time%]%NC% Cleaning caches...
for /r %%F in (*.pyc) do del "%%F" 2>NUL
for /d %%D in (__pycache__) do rmdir /S /Q "%%D" 2>NUL
rmdir /S /Q .pytest_cache 2>NUL

REM Handle watchdog restarts
if not "%RESTART_REASON%"=="manual" (
    echo %GREEN%[%date% %time%]%NC% Watchdog initiated restart - reason: %RESTART_REASON%
    echo %RESTART_REASON% > "%BOT_DIR%\data\flags\crash_detected"
)

REM Function to start the bot
echo %GREEN%[%date% %time%]%NC% Starting MalaBoT...

REM Ensure data directories exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%BOT_DIR%\data\flags" mkdir "%BOT_DIR%\data\flags"

REM Start bot in background
start "MalaBoT" /MIN %PYTHON_CMD% bot.py

echo %GREEN%[%date% %time%]%NC% MalaBoT started
echo %GREEN%[%date% %time%]%NC% Latest log file: data\logs\latest.log

REM Wait for startup
timeout /T 10 /NOBREAK >NUL

REM Verify startup
echo %GREEN%[%date% %time%]%NC% Verifying startup...

REM Check if process is running
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *bot.py*" | find "python.exe" >NUL
if %ERRORLEVEL%==0 (
    echo %GREEN%[%date% %time%]%NC% %GREEN%✅ MalaBoT is running successfully%NC%
) else (
    echo %RED%[%date% %time%]%NC% %RED%❌ MalaBoT is not running after startup%NC%
    echo %RED%[%date% %time%]%NC% Check logs for errors
    pause
    exit /b 1
)

REM Check latest log for startup message
if exist "%LOG_DIR%\latest.log" (
    findstr /C:"MalaBoT is now Locked in" "%LOG_DIR%\latest.log" >NUL
    if %ERRORLEVEL%==0 (
        echo %GREEN%[%date% %time%]%NC% %GREEN%✅ Startup verification passed%NC%
    ) else (
        echo %YELLOW%[%date% %time%]%NC% %YELLOW%⚠️ Startup verification inconclusive - check logs%NC%
    )
)

echo %GREEN%[%date% %time%]%NC% === MalaBoT Update Process Completed Successfully ===
echo %GREEN%[%date% %time%]%NC% Bot should be online and ready within 30 seconds

REM Check if owner alerts are enabled
if exist "%BOT_DIR%.env" (
    findstr /C:"OWNER_ALERTS_ENABLED=true" "%BOT_DIR%.env" >NUL
    if %ERRORLEVEL%==0 (
        echo %GREEN%[%date% %time%]%NC% Owner alerts are enabled - owner will be notified of restart
    )
)

echo %GREEN%[%date% %time%]%NC% Press any key to exit...
pause >NUL

exit /b 0