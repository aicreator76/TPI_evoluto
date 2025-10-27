@echo off

:: 1-installa_scheduler.cmd
::
:: This batch script registers a Windows scheduled task that runs a PowerShell
:: script (zip_log.ps1) every day at 19:00. The PowerShell script should
:: perform the ZIP backup and logging logic for DPI data. Adjust the
:: time or script path as needed. Running this script requires
:: administrative privileges.

REM Determine the directory of this script. The trailing backslash ensures
REM the PowerShell script path resolves correctly when concatenated.
set "SCRIPT_DIR=%~dp0"

REM Define the PowerShell script path. Make sure 'zip_log.ps1' exists in
REM the same folder as this CMD file. If you relocate the .ps1, update
REM the path accordingly.
set "PS_SCRIPT=%SCRIPT_DIR%zip_log.ps1"

echo.
echo Registering scheduled task "DPI_ZIP_LOG"...

REM Create or update the scheduled task. The /F flag forces the
REM replacement if the task already exists. The scheduled task runs
REM daily (SC DAILY) at 19:00 (ST 19:00) and invokes the PowerShell
REM engine with our script. "RL HIGHEST" ensures it runs with
REM highest privileges.
schtasks /Create /F ^
  /TN "DPI_ZIP_LOG" ^
  /SC DAILY ^
  /ST 19:00 ^
  /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"%PS_SCRIPT%\"" ^
  /RL HIGHEST

if %ERRORLEVEL% equ 0 (
    echo Scheduled task created successfully.
) else (
    echo Failed to create scheduled task. Please run this script as an administrator.
)

pause
