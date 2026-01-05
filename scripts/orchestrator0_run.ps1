param(
  [string]$Csv = "E:\CLONAZIONE\tpi_evoluto\data\dpi_sample.csv",
  [int]$HorizonDays = 60
)

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "E:\CLONAZIONE\LOG"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

python -m app.orchestrator.job --init-db --dpi-csv "$Csv" --horizon-days $HorizonDays --json `
  | Tee-Object -FilePath "$logDir\orchestrator0_$ts.json"

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
