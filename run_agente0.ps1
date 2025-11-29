Write-Host "=== Agente 0 - BLOCCO A: calcolo cruscotto DPI ==="
python "E:\CLONAZIONE\tpi_evoluto\agents\agente0_orchestratore\agente0_main.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Errore in BLOCCO A (agente0_main.py)." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "=== Agente 0 - BLOCCO B: feed notifiche n8n ==="
python "E:\CLONAZIONE\tpi_evoluto\agents\agente0_orchestratore\notifier_n8n.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Errore in BLOCCO B (notifier_n8n.py)." -ForegroundColor Yellow
    exit $LASTEXITCODE
}

Write-Host "=== Agente 0 completato: cruscotto e feed aggiornati ==="
