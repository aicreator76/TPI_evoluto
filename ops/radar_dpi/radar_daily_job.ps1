param(
  [string]$BaseDir = "E:\CLONAZIONE\REPORT_DELTA\RADAR_DPI_DATA",
  [string]$Tenant  = "default",
  [string]$Source  = "SCADENZIARIO_IIIa_CAT_2025-11-26",
  [string]$ApiBase = "http://127.0.0.1:8000/api"
)

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
