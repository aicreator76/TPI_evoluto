# --- AUTO-ELEVATION ---
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "== Setup TPI Finale ==" -ForegroundColor Cyan

# --- 1) Crea cartelle archivio ---
$ArchiveRoot = "D:\DesktopArchive"
$Folders = "Documenti","Immagini","Exe","Zip","Varie"
foreach ($f in $Folders) {
    $path = Join-Path $ArchiveRoot $f
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

# --- 2) Sposta file dal Desktop (tranne tpi_finale) ---
$Desktop = [Environment]::GetFolderPath("Desktop")
Get-ChildItem -Path $Desktop -File | ForEach-Object {
    if ($_.FullName -like "*tpi_finale*") { return }
    $ext = $_.Extension.ToLower()
    if (-not $ext) { Move-Item $_.FullName (Join-Path $ArchiveRoot "Varie") -Force; return }
    switch -Wildcard ($ext) {
        ".doc*" { Move-Item $_.FullName (Join-Path $ArchiveRoot "Documenti") -Force }
        ".pdf"  { Move-Item $_.FullName (Join-Path $ArchiveRoot "Documenti") -Force }
        ".txt"  { Move-Item $_.FullName (Join-Path $ArchiveRoot "Documenti") -Force }
        ".jpg"  { Move-Item $_.FullName (Join-Path $ArchiveRoot "Immagini") -Force }
        ".png"  { Move-Item $_.FullName (Join-Path $ArchiveRoot "Immagini") -Force }
        ".exe"  { Move-Item $_.FullName (Join-Path $ArchiveRoot "Exe") -Force }
        ".zip"  { Move-Item $_.FullName (Join-Path $ArchiveRoot "Zip") -Force }
        default { Move-Item $_.FullName (Join-Path $ArchiveRoot "Varie") -Force }
    }
}
Write-Host "File Desktop archiviati in $ArchiveRoot" -ForegroundColor Yellow

# --- 3) Setup progetto TPI ---
$Project = Join-Path $Desktop "tpi_finale\tpi_dashboard"
$Venv = Join-Path $Project ".venv"

if (-not (Test-Path $Venv)) {
    Write-Host "Creo virtualenv..." -ForegroundColor Yellow
    py -m venv $Venv
}
Write-Host "Attivo virtualenv..." -ForegroundColor Yellow
& "$Venv\Scripts\Activate.ps1"

# --- 4) Dipendenze ---
if (Test-Path "$Project\requirements.txt") {
    pip install -r "$Project\requirements.txt"
}

# --- 5) Avvio server Flask ---
Write-Host "== Avvio server su http://127.0.0.1:8000 ==" -ForegroundColor Green
Write-Host "Premi CTRL+C per fermare il server." -ForegroundColor Yellow
flask --app app run --host 127.0.0.1 --port 8000 --reload

# --- 6) Esito finale ---
Write-Host "== Esecuzione terminata con esito $LASTEXITCODE ==" -ForegroundColor Cyan
Pause

