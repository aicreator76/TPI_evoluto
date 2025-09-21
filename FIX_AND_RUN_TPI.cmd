@echo off
echo === FIX + RUN TPI_evoluto ===
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0FIX_AND_RUN_TPI.ps1"

echo.
echo Server FastAPI avviato su http://127.0.0.1:8000
echo Premi CTRL+C per chiudere il server.
pause
