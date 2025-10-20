@echo off

:: 2-start_cesarone.cmd
::
:: Launch the CESARONE print watcher script via AutoHotkey. This script
:: assumes that CESARONE_PrintWatcher.ahk resides in the same directory
:: as this batch file. Modify the variables below if the location
:: differs.

REM Determine the directory of this script. The trailing backslash ensures
REM the AHK script path resolves correctly when concatenated.
set "SCRIPT_DIR=%~dp0"

REM Define the AutoHotkey script. Ensure the CESARONE_PrintWatcher.ahk
REM script exists in this folder. Inside the AHK script, replace
REM `NOME_STAMPANTE` with the actual printer name before running.
set "AHK_SCRIPT=%SCRIPT_DIR%CESARONE_PrintWatcher.ahk"

REM Check if the AHK script exists
if not exist "%AHK_SCRIPT%" (
    echo Error: Could not find AutoHotkey script: %AHK_SCRIPT%
    echo Please ensure CESARONE_PrintWatcher.ahk is in the same directory.
    pause
    exit /b 1
)

REM Start the AutoHotkey script in a new window. The empty string "" ensures
REM the window uses the default title.
echo Starting CESARONE Print Watcher...
start "" "%AHK_SCRIPT%"

REM Confirm to the user
if %ERRORLEVEL% equ 0 (
    echo CESARONE Print Watcher started successfully.
) else (
    echo Failed to start the AutoHotkey script. Ensure AutoHotkey is installed and accessible in the PATH.
)

pause
