$ErrorActionPreference = "Stop"

$root = (git rev-parse --show-toplevel).Trim()
if (-not $root) { throw "Repo root not found" }
Set-Location $root

# Marker veri:
#   <<<<<<<
#   =======
#   >>>>>>>
# Nota: la riga di mezzo deve essere ESATTAMENTE 7 '='
$patterns = @(
  '^<<<<<<<',
  '^=======$',
  '^>>>>>>>'
)

$hits = New-Object System.Collections.Generic.List[string]

foreach($pat in $patterns){
  # git grep: exit 1 = nessun match (NON è errore)
  $out = & git grep -n --no-color -E $pat -- . 2>$null
  if ($out) { $hits.AddRange(@($out)) }
}

if ($hits.Count -gt 0) {
  Write-Host "❌ MERGE CONFLICT MARKERS TROVATI (blocca push)" -ForegroundColor Red
  ($hits | Sort-Object -Unique) | ForEach-Object { Write-Host $_ -ForegroundColor Red }
  exit 1
}

Write-Host "✅ OK: nessun merge conflict marker" -ForegroundColor Green
exit 0
