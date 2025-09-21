Write-Host "=== Avvio TPI_evoluto ===" -ForegroundColor Cyan

# Vai nella cartella del progetto
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

# Crea venv se non esiste
if (!(Test-Path ".\.venv")) {
    Write-Host "Creazione ambiente virtuale..." -ForegroundColor Yellow
    python -m venv .venv
}

# Attiva venv (ignora errori ExecutionPolicy se non parte)
try {
    . .\.venv\Scripts\Activate.ps1
} catch {
    Write-Host "⚠ Impossibile attivare venv via ps1 (ExecutionPolicy). Uso diretto di python.exe" -ForegroundColor Red
}

# Installa dipendenze
pip install --upgrade pip
pip install fastapi uvicorn jinja2

# Avvio server
Write-Host "Avvio server su http://127.0.0.1:8000 ..." -ForegroundColor Green
python -m uvicorn app.main:app --app-dir "." --host 127.0.0.1 --port 8000 --reload
