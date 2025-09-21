Write-Host "=== Fix dashboard templates + avvio TPI_evoluto ===" -ForegroundColor Cyan

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

function Write-Template($path, $content) {
    $dir = Split-Path $path -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Set-Content -Path $path -Value $content -Force -Encoding UTF8
    Write-Host "Template aggiornato: $path" -ForegroundColor Green
}

# === Funzione card generiche ===
function Get-CardsHTML($title, $items) {
@"
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>$title - TPI Evoluto</title>
  <link rel="stylesheet" href="/static/style.css">
  <style>
    .container { max-width: 1000px; margin: auto; padding: 20px; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
    .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
    .card h3 { margin-top: 0; color: #003366; }
    .card a { color: #0066cc; font-weight: bold; text-decoration: none; }
    .card a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <header><h1 style="background:#003366; color:white; padding:15px;">$title</h1></header>
  <main class="container">
    <div class="cards">
      $items
    </div>
  </main>
</body>
</html>
"@
}

# === Capitoli con Catalogo/Consegna/Revisioni ===
$sections = @{
    "dpi"            = "DPI"
    "sottogancio"    = "Sottogancio"
    "funi_metalliche"= "Funi metalliche"
    "funi_fibra"     = "Funi in fibra"
}

foreach ($key in $sections.Keys) {
    $title = $sections[$key]
    $items = @"
      <div class='card'><h3>📘 Catalogo</h3><p>Elenco prodotti e manuali CE.</p><a href='/$key/catalogo'>Vai</a></div>
      <div class='card'><h3>📦 Consegna</h3><p>Gestione consegne e scadenze.</p><a href='/$key/consegna'>Vai</a></div>
      <div class='card'><h3>🛠️ Revisioni</h3><p>Controlli e revisioni periodiche.</p><a href='/$key/revisioni'>Vai</a></div>
"@
    $html = Get-CardsHTML $title $items
    Write-Template "templates\$key.html" $html
}

# === Formazione con Corsi/Aggiornamenti/Certificazioni ===
$items_formazione = @"
  <div class='card'><h3>📚 Corsi</h3><p>Addestramento base e avanzato.</p><a href='/formazione/corsi'>Vai</a></div>
  <div class='card'><h3>📰 Aggiornamenti</h3><p>Normative e aggiornamenti obbligatori.</p><a href='/formazione/aggiornamenti'>Vai</a></div>
  <div class='card'><h3>✅ Certificazioni</h3><p>RSPP, preposti e lavoratori.</p><a href='/formazione/certificazioni'>Vai</a></div>
"@
$html_formazione = Get-CardsHTML "Formazione" $items_formazione
Write-Template "templates\formazione.html" $html_formazione

Write-Host "=== Tutti i capitoli aggiornati con dashboard ===" -ForegroundColor Cyan

# Avvio server
Write-Host "Avvio server su http://127.0.0.1:8000 ..." -ForegroundColor Green
python -m uvicorn app.main:app --app-dir "." --host 127.0.0.1 --port 8000 --reload
