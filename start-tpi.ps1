# start-tpi.ps1
Write-Host "=== Avvio Start-TPI con privilegi elevati ===" -ForegroundColor Cyan

# 🔹 Verifica se è in esecuzione come amministratore
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "⚠️ Riavvio come Amministratore..." -ForegroundColor Yellow
    Start-Process powershell "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# 🔹 Controlla se la porta 8000 è occupata e libera il processo
$port = 8000
$pid = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -Expand OwningProcess -First 1
if ($pid) {
    Write-Host "⚠️ Porta $port occupata, termino processo PID $pid..." -ForegroundColor Red
    Stop-Process -Id $pid -Force
    Start-Sleep -Seconds 2
}

# 🔹 Esegui SAFE_PUSH.ps1
Write-Host "✅ Porta libera. Avvio SAFE_PUSH.ps1" -ForegroundColor Green
powershell -ExecutionPolicy Bypass -File "C:\TPI_evoluto\SAFE_PUSH.ps1"
