Write-Host "=== Ripristino grafica classica + nuove funzionalità ===" -ForegroundColor Cyan

# 1. Sovrascrivi templates/index.html
@'
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ translations.title }}</title>
    <link rel="stylesheet" href="/static/theme.css">
</head>
<body>
    <header>
        <h1>{{ translations.welcome }}</h1>
        <nav>
            <a href="/">Home</a> |
            <a href="/dpi">DPI</a> |
            <a href="/sottogancio">Sottogancio</a> |
            <a href="/funi_metalliche">Funi Metalliche</a> |
            <a href="/funi_fibra">Funi Fibra</a> |
            <a href="/formazione">Formazione</a>
        </nav>
    </header>

    <main>
        <section>
            <h2>{{ translations.active_role }}: {{ active_role }}</h2>
            <form method="get" action="/">
                <label>{{ translations.select_role }}:</label>
                <select name="role">
                    <option value="datore">Datore</option>
                    <option value="revisore">Revisore</option>
                    <option value="rspp">RSPP</option>
                    <option value="lavoratore">Lavoratore</option>
                </select>
                <button type="submit">OK</button>
            </form>
        </section>

        <section>
            <h2>{{ translations.change_language }}</h2>
            <a href="/?lang=it">IT</a> |
            <a href="/?lang=en">EN</a> |
            <a href="/?lang=fr">FR</a> |
            <a href="/?lang=de">DE</a>
        </section>

        <section>
            <h2>Dashboard principali</h2>
            <ul>
                <li><a href="/dpi">Gestione DPI</a></li>
                <li><a href="/sottogancio">Gestione Sottogancio</a></li>
                <li><a href="/funi_metalliche">Gestione Funi Metalliche</a></li>
                <li><a href="/funi_fibra">Gestione Funi Fibra</a></li>
                <li><a href="/formazione">Gestione Formazione</a></li>
            </ul>
        </section>
    </main>
</body>
</html>
'@ | Set-Content "templates/index.html" -Encoding UTF8

# 2. Ripristina CSS leggibile
@'
body {
    font-family: Arial, sans-serif;
    margin: 20px;
    background: #f7f7f7;
    color: #222;
}
header {
    background: #004080;
    color: white;
    padding: 10px;
    border-radius: 8px;
}
nav a {
    color: white;
    margin: 0 10px;
    text-decoration: none;
}
nav a:hover {
    text-decoration: underline;
}
section {
    margin-top: 20px;
    padding: 15px;
    background: white;
    border: 1px solid #ccc;
    border-radius: 8px;
}
'@ | Set-Content "static/theme.css" -Encoding UTF8

# 3. Git commit + push
git add templates/index.html static/theme.css
git commit -m "fix(ui): ripristinata grafica classica con nuove funzionalità"
git push origin feature/logging-middleware

# 4. Avvio server
Write-Host "=== Avvio TPI_evoluto ===" -ForegroundColor Green
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
