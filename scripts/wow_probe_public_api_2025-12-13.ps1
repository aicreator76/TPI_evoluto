$ErrorActionPreference = "Continue"

$cfg = "E:\CLONAZIONE\tpi_evoluto\docs\demo_grafica_tpi_2025-12-10\config.js"
$candidates = New-Object System.Collections.Generic.List[string]

if (Test-Path $cfg) {
  $raw = Get-Content $cfg -Raw
  $m = [regex]::Match($raw, 'API_BASE\s*:\s*"([^"]+)"')
  if ($m.Success) { [void]$candidates.Add($m.Groups[1].Value.Trim()) }
}

# fallback noti
@(
  "https://tpi-evoluto-api.onrender.com",
  "https://tpi-api-staging.onrender.com"
) | ForEach-Object { if (-not $candidates.Contains($_)) { [void]$candidates.Add($_) } }

$paths = @(
  "/health",
  "/version",
  "/docs",
  "/openapi.json",
  "/api/health",
  "/api/version"
)

$origin = "https://aicreator76.github.io"
Write-Host "== WOW PROBE PUBLIC API =="
Write-Host "Origin CORS: $origin"
Write-Host ""

foreach ($base in $candidates) {
  if (-not $base) { continue }
  $base = $base.TrimEnd("/")

  Write-Host "---- BASE: $base ----"

  foreach ($p in $paths) {
    $u = "$base$p"
    try {
      $r = Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 8
      $snippet = ($r.Content | Select-Object -First 1)
      Write-Host ("GET  {0,-18}  {1} " -f $p, $r.StatusCode)
    } catch {
      if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
        $sc = [int]$_.Exception.Response.StatusCode
        Write-Host ("GET  {0,-18}  {1} " -f $p, $sc)
      } else {
        Write-Host ("GET  {0,-18}  ERR" -f $p)
      }
    }
  }

  # CORS OPTIONS su /health (se esiste) + / (fallback)
  foreach ($p in @("/health","/")) {
    $u = "$base$p"
    try {
      $opt = Invoke-WebRequest -UseBasicParsing -Method Options -Uri $u `
        -Headers @{ Origin=$origin; "Access-Control-Request-Method"="GET" } -TimeoutSec 8
      $aco = $opt.Headers["Access-Control-Allow-Origin"]
      Write-Host ("OPT {0,-18}  {1}  ACAO={2}" -f $p, $opt.StatusCode, $aco)
    } catch {
      Write-Host ("OPT {0,-18}  FAIL" -f $p)
    }
  }

  Write-Host ""
}

Write-Host "NOTE: se su /health vedi 404 ma /api/health è 200 => la UI deve chiamare /api/health (non /health)."
