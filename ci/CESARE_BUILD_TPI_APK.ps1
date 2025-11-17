# FILE: ci/CESARE_BUILD_TPI_APK.ps1
# Stub build APK per TPI (CI + locale)

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    [Parameter()]
    [string]$ReleaseRoot = ".\RELEASE_TPI",
    [switch]$CiMode
)

$ErrorActionPreference = "Stop"

Write-Host "=== CESARE BUILD TPI APK (CI) ===" -ForegroundColor Cyan
Write-Host "Version:     $Version"
Write-Host "ReleaseRoot: $ReleaseRoot"
Write-Host "CiMode:      $($CiMode.IsPresent)"

if (-not (Test-Path $ReleaseRoot)) {
    New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null
}

$dateBucket = Get-Date -Format "yyyy-MM-dd"
$apkDir     = Join-Path $ReleaseRoot $dateBucket
$apkDir     = Join-Path $apkDir "APK"

if (-not (Test-Path $apkDir)) {
    New-Item -ItemType Directory -Path $apkDir -Force | Out-Null
}

$stubName = "Camelot_TPI_{0}_APK-STUB.txt" -f $Version
$stubPath = Join-Path $apkDir $stubName

"Stub build APK per versione $Version (CiMode=$($CiMode.IsPresent))" |
    Set-Content -Path $stubPath -Encoding UTF8

Write-Host "Artefatto APK generato (STUB): $stubPath" -ForegroundColor Green
Write-Host "=== FINE CESARE BUILD TPI APK (CI) ===" -ForegroundColor Cyan
