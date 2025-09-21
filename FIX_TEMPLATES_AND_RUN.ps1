Write-Host "=== Ripristino vecchia grafica + nuove funzionalità ===" -ForegroundColor Cyan

# Cartella template
$tpl = "templates"

# Assicurati che la cartella templates esista
if (!(Test-Path $tpl)) { New-Item -ItemType Directory -Path $tpl }

# Home
@'
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>TPI Evoluto - Home</title>
</head>
<body>
  <h1>TPI — Teufelberger Protezione Individuale</h1>
  <p>Soluzioni per DPI, funi in acciaio e in fibra, accessori di sollevamento e formazione.</p>
  <ul>
    <li><a href="/dpi">DPI</a></li>
    <li><a href="/sottogancio">Sottogancio</a></li>
    <li><a href="/funi_metalliche">Funi in acciaio</a></li>
    <li><a href="/funi_fibra">Funi in fibra</a></li>
    <li><a href="/formazione">Formazione</a></li>
    <li><a href="/site">Chi siamo</a></li>
  </ul>
</body>
</html>
'@ | Set-Content "$tpl\index.html"

# DPI
@'
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><title>DPI</title></head>
<body>
  <h1>DPI</h1>
  <p>Gestione completa dei Dispositivi di Protezione Individuale.</p>
  <ul>
    <li><a href="/dpi/catalogo">Catalogo DPI</a></li>
    <li><a href="/dpi/consegna">Consegna DPI</a></li>
    <li><a href="/dpi/revisioni">Revisioni DPI</a></li>
  </ul>
</body>
</html>
'@ | Set-Content "$tpl\dpi.html"

# Sottogancio
@'
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><title>Sottogancio</title></head>
<body>
  <h1>Sottogancio</h1>
  <p>Accessori e sistemi di sollevamento sotto gancio.</p>
  <ul>
    <li><a href="/sottogancio/catalogo">Catalogo</a></li>
    <li><a href="/sottogancio/consegna">Consegna</a></li>
    <li><a href="/sottogancio/revisioni">Revisioni</a></li>
  </ul>
</body>
</html>
'@ | Set-Content "$tpl\sottogancio.html"

# Funi metalliche
@'
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><title>Funi in acciaio</title></head>
<body>
  <h1>Funi in acciaio</h1>
  <ul>
    <li><a href="/funi_metalliche/catalogo">Catalogo</a></li>
    <li><a href="/funi_metalliche/consegna">Consegna</a></li>
    <li><a href="/funi_metalliche/revisioni">Revisioni</a></li>
  </ul>
</body>
</html>
'@ | Set-Content "$tpl\funi_metalliche.html"

# Funi in fibra
@'
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><title>Funi in fibra</title></head>
<body>
  <h1>Funi in fibra</h1>
  <ul>
    <li><a href="/funi_fibra/catalogo">Catalogo</a></li>
    <li><a href="/funi_fibra/consegna">Consegna</a></li>
    <li><a href="/funi_fibra/revisioni">Revisioni</a></li>
  </ul>
</body>
</html>
'@ | Set-Content "$tpl\funi_fibra.html"

# Formazione
@'
<!DOCTYPE html>
<html lang="it">
<head><meta charset="UTF-8"><title>Formazione</title></head>
<body>
  <h1>Formazione</h1>
  <p>Programmi formativi e aggiornamenti normativi.</p>
  <ul>
    <li><a href="/formazione/corsi">Corsi</a></li>
    <li><a href="/formazione/aggiornamenti">Aggiornamenti</a></li>
    <li><a href="/formazione/certificazioni">Certificazioni</a></li>
  </ul>
</body>
</html>
'@ | Set-Content "$tpl\formazione.html"

Write-Host "=== Template aggiornati (vecchia grafica + nuove sezioni) ===" -ForegroundColor Green

# Avvio server
Write-Host "Avvio server su http://127.0.0.1:8000 ..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
