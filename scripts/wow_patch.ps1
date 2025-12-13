cd E:\CLONAZIONE\tpi_evoluto

@'
param(
  [Parameter(Mandatory=$true)][string]$ApiBase,
  [string]$Branch = ("pr/" + (Get-Date -Format "yyyy-MM-dd") + "-wow-api-online")
)

$ErrorActionPreference = "Stop"

$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root

$wowDir = Join-Path $root "docs\demo_grafica_tpi_2025-12-10"
$wowHtml = Join-Path $wowDir "dashboard_wow_dpi.html"
$configJs = Join-Path $wowDir "config.js"

if (!(Test-Path $wowHtml)) { throw "NON TROVO: $wowHtml" }

# 1) config.js
New-Item -ItemType Directory -Force $wowDir | Out-Null
@"
window.TPI_CONFIG = {
  API_BASE: "$ApiBase",
  REFRESH_MS: 8000
};
"@ | Set-Content -Encoding UTF8 $configJs

# 2) patch HTML
$html = Get-Content $wowHtml -Raw

# 2.1 include config.js (se manca)
if ($html -notmatch 'demo_grafica_tpi_2025-12-10/config\.js' -and $html -notmatch 'src="\./config\.js"') {
  $html = $html -replace '(</head>)', "  <script src=""./config.js""></script>`n`$1"
}

# 2.2 ensure placeholders IDs (se mancano)
if ($html -notmatch 'id="apiStatus"') {
  # prova a piazzarlo vicino a "Stato API" se esiste, altrimenti in fondo body
  if ($html -match 'Stato API') {
    $html = $html -replace '(Stato API.*?\n)', "`$1<span id=""apiStatus"">Offline</span> <span id=""apiVersion"">—</span>`n"
  } else {
    $html = $html -replace '(</body>)', "<div style=""display:none""><span id=""apiStatus"">Offline</span><span id=""apiVersion"">—</span></div>`n`$1"
  }
}

# 2.3 add WOW script + CSS (se manca marker)
$marker = "/* TPI_WOW_API_PATCH_v1 */"
if ($html -notmatch [regex]::Escape($marker)) {
  $payload = @"
<script>
$marker
(function(){
  const CFG = window.TPI_CONFIG || { API_BASE: "", REFRESH_MS: 8000 };
  const `$ = (s) => document.querySelector(s);

  function pulse(){
    const cards = document.querySelectorAll(".kpi-card, .panel, .card, .kpi");
    cards.forEach(c => { c.classList.remove("pulse"); void c.offsetWidth; c.classList.add("pulse"); });
  }

  function setApiState(ok, payload) {
    const el = `$`("#apiStatus");
    const ver = `$`("#apiVersion");
    if (!el) return;

    if (ok) {
      el.textContent = "Online";
      el.classList.add("ok");
      el.classList.remove("bad");
      if (ver) ver.textContent = payload ? JSON.stringify(payload) : "OK";
      pulse();
    } else {
      el.textContent = "Offline";
      el.classList.add("bad");
      el.classList.remove("ok");
      if (ver) ver.textContent = "—";
    }
  }

  async function ping(){
    try{
      if (!CFG.API_BASE) throw new Error("no API_BASE");
      const base = CFG.API_BASE.replace(/\/$/,"");
      const r = await fetch(base + "/health", { cache: "no-store" });
      if(!r.ok) throw new Error("HTTP " + r.status);
      const j = await r.json();
      setApiState(true, j);
    }catch(e){
      setApiState(false);
    }
  }

  async function loop(){
    await ping();
    setTimeout(loop, CFG.REFRESH_MS || 8000);
  }

  loop();
})();
</script>

<style>
  .ok { color:#29f2a6 !important; font-weight:800; }
  .bad { color:#49b6ff !important; font-weight:800; }
  .pulse { animation: pulseGlow 0.9s ease-in-out; }
  @keyframes pulseGlow {
    0% { transform: translateY(0); filter: brightness(1); }
    50% { transform: translateY(-2px); filter: brightness(1.15); }
    100% { transform: translateY(0); filter: brightness(1); }
  }
</style>
"@

  $html = $html -replace '(</body>)', "$payload`n`$1"
}

Set-Content -Encoding UTF8 $wowHtml $html

# 3) Git flow
git switch main | Out-Null
git pull | Out-Null

git switch -c $Branch | Out-Null

pre-commit run -a | Out-Null

git add -A
git commit -m "feat(wow): API online + pulse (auto patch)" | Out-Null
git push -u origin $Branch | Out-Null

gh pr create --base main --head $Branch --title "feat(wow): API online + pulse" --body "Auto patch dashboard_wow_dpi.html + config.js. /health ping + animazioni." | Out-Null

Write-Host ""
Write-Host "OK. PR CREATA. Ora fai merge admin:" -ForegroundColor Green
Write-Host "  gh pr merge --squash --delete-branch --admin" -ForegroundColor Yellow
Write-Host ""
Write-Host "LINK (dopo merge + Pages):" -ForegroundColor Green
Write-Host "  https://aicreator76.github.io/TPI_evoluto/demo_grafica_tpi_2025-12-10/dashboard_wow_dpi.html" -ForegroundColor Cyan
'@ | Set-Content -Encoding UTF8 .\scripts\wow_patch.ps1
