param(
  [Parameter(Mandatory=$true)][string]$ApiBase
)

$ErrorActionPreference="Stop"
$cfg="E:\CLONAZIONE\tpi_evoluto\docs\demo_grafica_tpi_2025-12-10\config.js"
if(-not (Test-Path $cfg)){ throw "Manca config.js: $cfg" }

$raw = Get-Content $cfg -Raw
$api = $ApiBase.TrimEnd("/")

if($raw -match 'API_BASE\s*:\s*".*?"'){
  $raw = [regex]::Replace($raw,'API_BASE\s*:\s*".*?"',"API_BASE: `"$api`"")
} else {
  $raw = "window.TPI_CONFIG = {`n  API_BASE: `"$api`",`n  REFRESH_MS: 8000`n};`n"
}

Set-Content -Path $cfg -Value $raw -Encoding UTF8
Write-Host "OK: API_BASE impostata a $api"
Write-Host "File: $cfg"
