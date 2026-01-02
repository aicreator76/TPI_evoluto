param(
    [string]$WorkDir = "E:\CLONAZIONE\tpi_evoluto\catalogo_work",
    [string]$OutZip  = "E:\CLONAZIONE\tpi_evoluto\RELEASE_TPI\catalogo\catalogo_tpi_lynx_v1.zip"
)

Write-Host "=== BUILD CATALOGO TPI ZIP ==="

if (!(Test-Path $WorkDir)) { New-Item -ItemType Directory -Path $WorkDir | Out-Null }
if (!(Test-Path (Split-Path $OutZip))) { New-Item -ItemType Directory -Path (Split-Path $OutZip) | Out-Null }

# pulizia cartella lavoro
Get-ChildItem $WorkDir -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue

Copy-Item ".\docs\catalogo\catalogo_tpi.csv"   "$WorkDir\" -Force
Copy-Item ".\docs\catalogo\catalogo_tpi.md"    "$WorkDir\" -Force
Copy-Item ".\docs\catalogo\catalogo_tpi.json"  "$WorkDir\" -Force
Copy-Item ".\docs\catalogo\README_LYNX.txt"    "$WorkDir\" -Force

if (Test-Path ".\docs\catalogo\img") {
    Copy-Item ".\docs\catalogo\img" "$WorkDir\img" -Recurse -Force
}

Compress-Archive -Path "$WorkDir\*" -DestinationPath $OutZip -Force

Write-Host "ZIP creato con successo:"
Write-Host $OutZip
