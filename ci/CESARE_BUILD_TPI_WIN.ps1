# FILE: ci/CESARE_BUILD_TPI_WIN.ps1
# Stub build Windows per TPI (CI + locale)

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    [Parameter()]
    [string]$ReleaseRoot = ".\RELEASE_TPI",
    [switch]$CiMode
)

$ErrorActionPreference = "Stop"

Write-Host "=== CESARE BUILD TPI WIN (CI) ===" -ForegroundColor Cyan
Write-Host "Version:     $Version"
Write-Host "ReleaseRoot: $ReleaseRoot"
Write-Host "CiMode:      $($CiMode.IsPresent)"

if (-not (Test-Path $ReleaseRoot)) {
    New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null
}

$dateBucket = Get-Date -Format "yyyy-MM-dd"
$winDir     = Join-Path $ReleaseRoot $dateBucket
$winDir     = Join-Path $winDir "WIN"

if (-not (Test-Path $winDir)) {
    New-Item -ItemType Directory -Path $winDir -Force | Out-Null
}

$stubName = "Camelot_TPI_{0}_WIN-STUB.txt" -f $Version
$stubPath = Join-Path $winDir $stubName

"Stub build WIN per versione $Version (CiMode=$($CiMode.IsPresent))" |
    Set-Content -Path $stubPath -Encoding UTF8

Write-Host "Artefatto Windows generato (STUB): $stubPath" -ForegroundColor Green
Write-Host "=== FINE CESARE BUILD TPI WIN (CI) ===" -ForegroundColor Cyan
