# ============================================
# Script di supporto – diff TPI_evoluto vs TPI_api_staging
# Da lanciare MANUALMENTE in PowerShell.
# Percorsi COMPLETI, pronti da copiare.
# ============================================

$repoEvoluto = "E:\CLONAZIONE\tpi_evoluto"
$repoStaging = "E:\CLONAZIONE\TPI_api_staging"  # MODIFICA QUI SE SERVE

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " DIFF TPI_evoluto vs TPI_api_staging" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Repo EVOLUTO : $repoEvoluto"
Write-Host "Repo STAGING : $repoStaging"
Write-Host ""

# 1) STRUTTURA CARTELLE (ALTO LIVELLO)
Write-Host "1) Differenze a livello di struttura cartelle (alto livello):" -ForegroundColor Yellow
Write-Host "   Compare-Object -ReferenceObject (Get-ChildItem 'E:\CLONAZIONE\tpi_evoluto' | Select-Object Name) -DifferenceObject (Get-ChildItem 'E:\CLONAZIONE\TPI_api_staging' | Select-Object Name)"
Write-Host ""

# 2) DIFF GIT DI ENTRAMBI I REPO
Write-Host "2) Diff Git dei progetti (stat sintetico):" -ForegroundColor Yellow
Write-Host "   git -C 'E:\CLONAZIONE\tpi_evoluto' diff --stat"
Write-Host "   git -C 'E:\CLONAZIONE\TPI_api_staging' diff --stat"
Write-Host ""

# 3) ELENCO FILE .PY
Write-Host "3) Elenco file .py in entrambi per confronto mirato:" -ForegroundColor Yellow
Write-Host "   Get-ChildItem 'E:\CLONAZIONE\tpi_evoluto' -Recurse -Filter *.py | Select-Object FullName"
Write-Host "   Get-ChildItem 'E:\CLONAZIONE\TPI_api_staging' -Recurse -Filter *.py | Select-Object FullName"
Write-Host ""

Write-Host "Usa questi comandi così come sono (già con percorsi completi) e incolla i risultati nei .md di unificazione." -ForegroundColor Cyan
