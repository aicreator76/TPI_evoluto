$ErrorActionPreference = "Stop"

$root = (git rev-parse --show-toplevel).Trim()
if (-not $root) { throw "Repo root not found" }

$files = git ls-files
if (-not $files) { exit 0 }

$files = $files | Where-Object { $_ -notmatch '\.(png|jpg|jpeg|gif|pdf|zip|exe|apk)$' }
$paths = $files | ForEach-Object { Join-Path $root $_ }

$pattern = '^(<{7}|={7}|>{7})'

$hits = Select-String -Path $paths -Pattern $pattern -AllMatches -ErrorAction SilentlyContinue
if ($hits) {
  Write-Host "❌ MERGE MARKERS TROVATI (blocca push)" -ForegroundColor Red
  $hits | Select-Object Path, LineNumber, Line | Format-Table -AutoSize
  exit 1
}

Write-Host "✅ OK: nessun merge marker" -ForegroundColor Green
exit 0
