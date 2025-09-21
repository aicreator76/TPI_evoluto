Write-Host "=== Fix templates + avvio TPI_evoluto ===" -ForegroundColor Cyan

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)

function Write-Template($path, $content) {
    $dir = Split-Path $path -Parent
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Set-Content -Path $path -Value $content -Force -Encoding UTF8
    Write-Host "Template aggiornato: $path" -ForegroundColor Green
}

# --- DPI (home sezione) ---
$tpl_dpi = @"
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>DPI - TPI Evoluto</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><h1>DPI</h1></header>
  <main>
    <p>Gestione completa dei Dispositivi di Protezione Individuale.</p>
    <ul>
      <li><a href="/dpi/catalogo">Catalogo DPI</a></li>
      <li><a href="/dpi/consegna">Consegna DPI</a></li>
      <li><a href="/dpi/revisioni">Revisioni DPI</a></li>
    </ul>
  </main>
</body>
</html>
"@
Write-Template "templates\dpi.html" $tpl_dpi

# --- Sottocapitolo: Catalogo ---
$tpl_catalogo = @"
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Catalogo DPI - TPI Evoluto</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><h1>Catalogo DPI</h1></header>
  <main>
    <p>Elenco dei principali DPI con schede tecniche:</p>
    <ul>
      <li>Caschi di protezione (EN 397)</li>
      <li>Imbracature anticaduta (EN 361)</li>
      <li>Occhiali protettivi (EN 166)</li>
      <li>Guanti da lavoro (EN 388)</li>
    </ul>
  </main>
</body>
</html>
"@
Write-Template "templates\dpi_catalogo.html" $tpl_catalogo

# --- Sottocapitolo: Consegna ---
$tpl_consegna = @"
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Consegna DPI - TPI Evoluto</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><h1>Consegna DPI</h1></header>
  <main>
    <p>Gestione delle consegne ai lavoratori:</p>
    <ul>
      <li>Assegnazione DPI per reparto/matricola</li>
      <li>Storico consegne con firma digitale</li>
      <li>Report scadenze sostituzioni</li>
    </ul>
  </main>
</body>
</html>
"@
Write-Template "templates\dpi_consegna.html" $tpl_consegna

# --- Sottocapitolo: Revisioni ---
$tpl_revisioni = @"
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Revisioni DPI - TPI Evoluto</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header><h1>Revisioni DPI</h1></header>
  <main>
    <p>Funzionalità per controlli e revisioni periodiche:</p>
    <ul>
      <li>Scadenziario controlli obbligatori</li>
      <li>Registrazione esiti revisione</li>
      <li>Notifiche automatiche revisione imminente</li>
    </ul>
  </main>
</body>
</html>
"@
Write-Template "templates\dpi_revisioni.html" $tpl_revisioni

Write-Host "=== Tutti i template DPI sono presenti e aggiornati ===" -ForegroundColor Cyan

# --- Avvio server ---
Write-Host "Avvio server su http://127.0.0.1:8000 ..." -ForegroundColor Green
python -m uvicorn app.main:app --app-dir "." --host 127.0.0.1 --port 8000 --reload
