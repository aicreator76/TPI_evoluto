$ErrorActionPreference = "Stop"
$root = "E:\CLONAZIONE\tpi_evoluto"
Set-Location $root

$env:ORCH_OWNER = "TPI-TaskScheduler"
$csv = "E:\CLONAZIONE\tpi_evoluto\data\dpi_sample.csv"

$logDir = Join-Path $root "LOG"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir ("orchestrator0_{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

python -m app.orchestrator.job --init-db --dpi-csv $csv --horizon-days 60 --json --lock-name orchestrator0 --lock-ttl-seconds 900 2>&1 |
  Tee-Object -FilePath $logFile -Append

exit $LASTEXITCODE
