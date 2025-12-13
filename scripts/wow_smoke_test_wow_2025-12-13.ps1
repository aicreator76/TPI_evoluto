$ErrorActionPreference = "Stop"

$root = "https://aicreator76.github.io/TPI_evoluto/demo_grafica_tpi_2025-12-10"
$urls = @(
  "https://aicreator76.github.io/TPI_evoluto/",
  "$root/dashboard_wow_dpi.html",
  "$root/config.js",
  "$root/wow_anim.css",
  "$root/wow_photo.css",
  "$root/wow_photo_overlay.js",
  "$root/data/wow_ui.js",
  "$root/data/demo_cataloghi.js",
  "$root/data/demo_movimenti.js"
)

Write-Host "=== WOW SMOKE TEST (PAGES) ==="
foreach ($u in $urls) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 12
    Write-Host ("{0}  {1}" -f $r.StatusCode, $u)
  } catch {
    Write-Host ("FAIL {0}" -f $u)
    throw
  }
}

# apri dashboard con cache buster
$buster = Get-Date -Format yyyyMMddHHmmss
Start-Process "msedge.exe" "$root/dashboard_wow_dpi.html?v=$buster"

Write-Host "OK: aperto Edge con cache-buster v=$buster"
