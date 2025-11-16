param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,
    [Parameter(Mandatory=$true)]
    [string]$ReleaseRoot,
    [Parameter(Mandatory=$true)]
    [string]$Date,
    [Parameter(Mandatory=$true)]
    [string]$Version
)

Write-Host "=== Build-TPI-WIN ==="
Write-Host "ProjectRoot = $ProjectRoot"
Write-Host "ReleaseRoot = $ReleaseRoot"
Write-Host "Date        = $Date"
Write-Host "Version     = $Version"

# Cartella output: RELEASE_TPI\<DATA>\WIN
$winOut = Join-Path $ReleaseRoot (Join-Path $Date "WIN")
New-Item -ItemType Directory -Path $winOut -Force | Out-Null

# Per ora: artefatto placeholder (da sostituire con build reale Flutter)
$exeName = "Camelot_TPI_{0}-WIN.exe" -f $Version
$exePath = Join-Path $winOut $exeName

"Placeholder build Windows per TPI (ver. $Version, data $Date)" | Set-Content -Path $exePath -Encoding UTF8

Write-Host "Creato artefatto WIN placeholder: $exePath"
