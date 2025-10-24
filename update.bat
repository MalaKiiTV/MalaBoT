@echo off
setlocal enabledelayedexpansion
title MalaBoT Update Script

:: Configuration
set "BOT_DIR=%~dp0"
set "VENV_DIR=%BOT_DIR%venv"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "LOG_DIR=%BOT_DIR%data\logs"
set "BACKUP_DIR=%BOT_DIR%backups"
set "TIMESTAMP=%date:~-4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "UPDATE_LOG=%LOG_DIR%\update_%TIMESTAMP%.log"

:: Create log directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Start logging
echo ============================================================ > "%UPDATE_LOG%"
echo MalaBoT Update Script >> "%UPDATE_LOG%"
echo Started: %date% %time% >> "%UPDATE_LOG%"
echo ============================================================ >> "%UPDATE_LOG%"
echo.

echo [INFO] Starting MalaBoT update process...
echo [INFO] Update log: %UPDATE_LOG%
echo.

:: Stop the bot if it's running
echo [INFO] Checking for running bot processes...
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq MalaBoT*" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Stopping MalaBoT process...
    taskkill /FI "WINDOWTITLE eq MalaBoT*" /F >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo [INFO] Bot stopped
) else (
    echo [INFO] No running bot process found
)

:: Create backups
echo [INFO] Creating backups...
if not exist "%BACKUP_DIR%\logs" mkdir "%BACKUP_DIR%\logs"
if exist "%LOG_DIR%\*.log" (
    xcopy "%LOG_DIR%\*.log" "%BACKUP_DIR%\logs\%TIMESTAMP%&quot; /Y /Q >nul 2>&1
    echo [INFO] Logs backed up
)

:: Update from Git if repository exists
if exist ".git" (
    echo [INFO] Updating from Git repository...
    git pull >> "%UPDATE_LOG%" 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Git pull successful
    ) else (
        echo [WARN] Git pull failed or no changes
    )
) else (
    echo [INFO] Not a Git repository, skipping Git update
)

:: Activate virtual environment or create it
if not exist "%VENV_DIR%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%" >> "%UPDATE_LOG%" 2>&1
)

echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Update pip
echo [INFO] Updating pip...
python -m pip install --upgrade pip >> "%UPDATE_LOG%" 2>&1

:: Install/update dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt >> "%UPDATE_LOG%" 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Dependencies installed successfully
) else (
    echo [ERROR] Failed to install dependencies
    echo [ERROR] Check %UPDATE_LOG% for details
    pause
    exit /b 1
)

:: Clean old backups (keep last 7 days)
echo [INFO] Cleaning old backups...
forfiles /P "%BACKUP_DIR%\logs" /D -7 /C "cmd /c if @isdir==TRUE rmdir /S /Q @path" 2>nul

:: Clean cache
echo [INFO] Cleaning caches...
if exist "__pycache__" rmdir /S /Q "__pycache__" 2>nul
if exist "cogs\__pycache__" rmdir /S /Q "cogs\__pycache__" 2>nul
if exist "utils\__pycache__" rmdir /S /Q "utils\__pycache__" 2>nul
if exist "config\__pycache__" rmdir /S /Q "config\__pycache__" 2>nul
if exist "database\__pycache__" rmdir /S /Q "database\__pycache__" 2>nul

:: Start the bot
echo.
echo [INFO] Starting MalaBoT...
start "MalaBoT" /MIN "%PYTHON%" bot.py
timeout /t 3 /nobreak >nul

:: Verify bot started
echo [INFO] Verifying bot startup...
timeout /t 5 /nobreak >nul

:: Check if bot is running by looking for the process
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] ✅ MalaBoT is running
    echo [INFO] Check data\logs\latest.log for bot status
) else (
    echo [WARN] Could not verify bot process
    echo [WARN] Check data\logs\latest.log for any errors
)

echo.
echo [INFO] Update complete!
echo [INFO] Full log: %UPDATE_LOG%
echo.
echo ============================================================
echo Update completed: %date% %time% >> "%UPDATE_LOG%"
echo ============================================================ >> "%UPDATE_LOG%"

pause