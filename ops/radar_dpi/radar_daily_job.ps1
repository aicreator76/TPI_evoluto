param(
  [string]$BaseDir = "",
  [string]$Tenant  = "default",
  [string]$Source  = "SCADENZIARIO_IIIa_CAT_2025-11-26",
  [string]$ApiBase = ""
)

# Defaults via ENV (no hardcoded paths)
if([string]::IsNullOrWhiteSpace($BaseDir)){
  $BaseDir = $env:RADAR_DPI_DATA_DIR
}
if([string]::IsNullOrWhiteSpace($BaseDir)){
  $BaseDir = Join-Path $PSScriptRoot "RADAR_DPI_DATA"
}

if([string]::IsNullOrWhiteSpace($ApiBase)){
  $ApiBase = $env:RADAR_API_BASE
}
if([string]::IsNullOrWhiteSpace($ApiBase)){
  $ApiBase = "https://tpi-evoluto-staging.onrender.com/api"
}

$repDir = Join-Path $BaseDir "reports"
New-Item -ItemType Directory -Force -Path $repDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"

$csvOut  = Join-Path $repDir ("radar_{0}_{1}.csv"  -f $Source,$stamp)
$jsonOut = Join-Path $repDir ("radar_{0}_{1}.json" -f $Source,$stamp)

# CSV
curl.exe -s "$ApiBase/radar/report.csv?tenant=$Tenant&source=$Source" -o $csvOut | Out-Null

# JSON (scadenze)
curl.exe -s "$ApiBase/radar/scadenze?tenant=$Tenant&source=$Source&limit=2000" -o $jsonOut | Out-Null

"OK JOB -> CSV=$csvOut | JSON=$jsonOut"
