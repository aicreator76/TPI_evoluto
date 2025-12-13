$ErrorActionPreference = "Stop"

$base = "E:\CLONAZIONE\tpi_evoluto\docs\demo_grafica_tpi_2025-12-10"
$imgDir = Join-Path $base "assets\img"
New-Item -ItemType Directory -Force $imgDir | Out-Null

# sorgenti da cui estrarre codici
$sources = @(
  Join-Path $base "data\demo_cataloghi.js",
  Join-Path $base "dashboard_wow_dpi.html",
  Join-Path $base "home_demo_tpi_api.html",
  Join-Path $base "home_demo_accessori_api.html"
) | Where-Object { Test-Path $_ }

if (-not $sources) { throw "Nessuna sorgente trovata per estrarre i codici (demo_cataloghi.js / html)." }

$rx = [regex]'\b(DPI|ACC|SOT|SG|IMB|ELM|FUN)[A-Z0-9-]*-[A-Z0-9-]+\b'
$codes = New-Object System.Collections.Generic.HashSet[string]

foreach ($s in $sources) {
  $txt = Get-Content $s -Raw
  foreach ($m in $rx.Matches($txt)) { [void]$codes.Add($m.Value) }
}

if ($codes.Count -eq 0) { throw "Non ho trovato codici articolo nelle sorgenti (regex). Controlla demo_cataloghi.js." }

function New-DemoSvg([string]$code, [string]$outPath) {
@"
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b1220"/>
      <stop offset="1" stop-color="#162a4a"/>
    </linearGradient>
    <radialGradient id="r" cx="35%" cy="30%" r="60%">
      <stop offset="0" stop-color="rgba(0,255,191,0.35)"/>
      <stop offset="1" stop-color="rgba(0,255,191,0.0)"/>
    </radialGradient>
  </defs>
  <rect width="900" height="500" rx="34" fill="url(#g)"/>
  <rect x="0" y="0" width="900" height="500" rx="34" fill="url(#r)"/>
  <text x="50" y="115" font-family="Arial" font-size="44" fill="#cfe2ff" font-weight="700">TPI • Foto Demo</text>
  <text x="50" y="185" font-family="Arial" font-size="26" fill="#9fb3d1">Sostituisci questo SVG con una foto reale (PNG/JPG/WebP)</text>
  <rect x="50" y="250" width="800" height="170" rx="26" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.12)"/>
  <text x="85" y="330" font-family="Consolas, Arial" font-size="48" fill="#00ffbf" font-weight="700">$code</text>
  <text x="85" y="385" font-family="Arial" font-size="20" fill="#cfe2ff">Numero articolo</text>
</svg>
"@ | Set-Content -Path $outPath -Encoding UTF8
}

Write-Host "== WOW DEMO IMAGES =="
Write-Host ("Codici trovati: " + $codes.Count)

foreach ($c in $codes) {
  $safe = ($c -replace '[^\w\-\.]','_')
  $out  = Join-Path $imgDir "$safe.svg"
  if (-not (Test-Path $out)) {
    New-DemoSvg -code $c -outPath $out
    Write-Host "CREATO  $out"
  } else {
    Write-Host "OK      $out"
  }
}

Write-Host "DONE: immagini demo pronte in $imgDir"
