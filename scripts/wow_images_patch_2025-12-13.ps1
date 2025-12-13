param(
  [string]$Repo = "E:\CLONAZIONE\tpi_evoluto",
  [string]$Demo = "E:\CLONAZIONE\tpi_evoluto\docs\demo_grafica_tpi_2025-12-10",
  [string]$ApiBase = "https://tpi-api-staging.onrender.com"
)

$ErrorActionPreference="Stop"
$Data = Join-Path $Demo "data"
$Assets = Join-Path $Demo "assets\img"
New-Item -ItemType Directory -Force $Assets | Out-Null

# 1) FIX API_BASE (config.js)
$config = Join-Path $Demo "config.js"
if(Test-Path $config){
  $raw = Get-Content $config -Raw
  $raw2 = $raw -replace 'API_BASE:\s*"[^"]+"', ('API_BASE: "'+$ApiBase+'"')
  if($raw2 -ne $raw){
    Copy-Item $config ($config+".bak_2025-12-13") -Force
    Set-Content -Path $config -Value $raw2 -Encoding UTF8
  }
}

# 2) Trova immagini catalogo (IMG_<codice>.* oppure <codice>.*) SOTTO docs\
$searchRoot = Join-Path $Repo "docs"
$imgs = Get-ChildItem $searchRoot -Recurse -Include *.png,*.jpg,*.jpeg,*.webp -ErrorAction SilentlyContinue

$map = [ordered]@{}
foreach($f in $imgs){
  $name = [IO.Path]::GetFileNameWithoutExtension($f.Name)

  # estrai codice
  $code = $null
  if($name -match '^IMG[_-](.+)$'){ $code = $Matches[1] }
  elseif($name -match '^(DPI|ACC|SOT)[-_].+$'){ $code = $name }
  else { continue }

  # normalizza (underscore -> hyphen)
  $code = $code -replace '_','-'

  # copia in assets con nome canonico
  $ext = $f.Extension.ToLower()
  $destName = "IMG_$code$ext"
  $dest = Join-Path $Assets $destName
  if(-not (Test-Path $dest)){
    Copy-Item $f.FullName $dest -Force
  }

  # path relativo per Pages
  $map[$code] = "./assets/img/$destName"
}

# 3) Scrivi images_map.js
$mapFile = Join-Path $Data "images_map.js"
$lines = @()
$lines += "window.TPI_IMAGES = window.TPI_IMAGES || {};"
foreach($k in $map.Keys){
  $v = $map[$k]
  $lines += ('window.TPI_IMAGES["{0}"] = "{1}";' -f $k, $v)
}
Set-Content -Path $mapFile -Value ($lines -join "`n") -Encoding UTF8

# 4) Hook WOW (inietta IMG nel dettaglio senza toccare wow_ui.js)
$hook = Join-Path $Data "wow_images_hook.js"
@"
(function(){
  function pickCode(){
    // trova un testo tipo DPI-XXX-001 dentro al dettaglio
    const all = Array.from(document.querySelectorAll('div,span,h1,h2,h3'));
    const hit = all.find(x => x.textContent && x.textContent.trim().match(/^(DPI|ACC|SOT)[-][A-Z0-9]+[-][0-9]+/));
    if(!hit) return null;
    return hit.textContent.trim().match(/^(DPI|ACC|SOT)[-][A-Z0-9]+[-][0-9]+/)[0];
  }
  function ensureImg(){
    const code = pickCode();
    if(!code) return;

    const url = (window.TPI_IMAGES||{})[code];
    if(!url) return;

    // cerca il pannello dettaglio (quello che contiene "TIMELINE REVISIONI / EVENTI")
    const nodes = Array.from(document.querySelectorAll('div'));
    const t = nodes.find(n => (n.textContent||"").includes("TIMELINE REVISIONI / EVENTI"));
    if(!t) return;

    // radice: un contenitore grande vicino alla timeline
    const root = t.closest('div');
    if(!root) return;

    if(root.querySelector('[data-wow-img="1"]')) return;

    const img = document.createElement("img");
    img.src = url;
    img.alt = code;
    img.setAttribute("data-wow-img","1");
    img.style.width="220px";
    img.style.maxWidth="35%";
    img.style.borderRadius="14px";
    img.style.margin="0 16px 12px 0";
    img.style.boxShadow="0 10px 30px rgba(0,0,0,.35)";
    img.style.objectFit="cover";

    // inserisci prima del blocco timeline
    const wrap = document.createElement("div");
    wrap.style.display="flex";
    wrap.style.alignItems="flex-start";
    wrap.style.gap="12px";

    const parent = root.parentElement;
    if(!parent) return;

    // prova a mettere immagine nella colonna sinistra del dettaglio (prima della timeline)
    wrap.appendChild(img);
    wrap.appendChild(root.cloneNode(true));
    parent.replaceChild(wrap, root);
  }

  // osserva cambi DOM (quando apri un dettaglio)
  const obs = new MutationObserver(() => ensureImg());
  obs.observe(document.documentElement, {childList:true, subtree:true});
  document.addEventListener("click", () => setTimeout(ensureImg, 150));
  window.addEventListener("load", () => setTimeout(ensureImg, 300));
})();
"@ | Set-Content -Path $hook -Encoding UTF8

# 5) Includi scripts in dashboard_wow_dpi.html
$html = Join-Path $Demo "dashboard_wow_dpi.html"
if(Test-Path $html){
  $h = Get-Content $html -Raw
  if($h -notmatch 'images_map\.js'){
    $h = $h -replace '(<script src="\./data/wow_ui\.js"></script>)', "<script src=`"./data/images_map.js`"></script>`n`$1"
  }
  if($h -notmatch 'wow_images_hook\.js'){
    $h = $h -replace '(<script src="\./data/wow_ui\.js"></script>)', "`$1`n<script src=`"./data/wow_images_hook.js`"></script>"
  }
  Copy-Item $html ($html+".bak_2025-12-13") -Force
  Set-Content -Path $html -Value $h -Encoding UTF8
}

Write-Host "OK: API_BASE fix + images_map + hook + dashboard patched"
Write-Host "Immagini mappate:" $map.Count
