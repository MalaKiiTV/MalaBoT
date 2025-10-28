@echo off
REM Fix stuck merge state

echo ========================================
echo Fixing Stuck Merge State
echo ========================================
echo.

echo [1/3] Aborting any pending merge...
git merge --abort 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Merge aborted
) else (
    echo [INFO] No merge to abort
)

echo [2/3] Cleaning up merge files...
if exist .git\MERGE_HEAD del /F .git\MERGE_HEAD 2>nul
if exist .git\MERGE_MODE del /F .git\MERGE_MODE 2>nul
if exist .git\MERGE_MSG del /F .git\MERGE_MSG 2>nul
echo [SUCCESS] Merge files cleaned

echo [3/3] Configuring git to prevent future issues...
git config pull.rebase false
git config merge.commit no
git config core.editor "echo"
echo [SUCCESS] Git configured

echo.
echo ========================================
echo [SUCCESS] Merge state fixed!
echo ========================================
echo.
echo You can now use dev.bat option 14 to pull.
echo.
pause