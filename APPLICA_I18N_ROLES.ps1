# === Script: APPLICA_I18N_ROLES.ps1 ===
Write-Host "=== Creazione struttura i18n + ruoli ===" -ForegroundColor Cyan

# Percorso progetto
$proj = "C:\TPI_evoluto"

# Cartelle necessarie
$folders = @(
    "$proj\app\config",
    "$proj\locales",
    "$proj\templates",
    "$proj\static"
)

foreach ($f in $folders) {
    if (-not (Test-Path $f)) {
        New-Item -ItemType Directory -Path $f | Out-Null
        Write-Host "Creata cartella: $f"
    }
}

# ---------------------------
# FILE: app/main.py
# ---------------------------
@'
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config.roles import UserRole

app = FastAPI(title="TPI_evoluto")

templates = Jinja2Templates(directory="templates")

def load_translations(lang: str):
    path = os.path.join("locales", f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join("locales", "it.json")  # fallback
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, lang: str = "it", role: str = UserRole.datore):
    translations = load_translations(lang)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "translations": translations,
            "lang": lang,
            "role": role
        }
    )
'@ | Set-Content "$proj\app\main.py" -Encoding UTF8

# ---------------------------
# FILE: app/config/roles.py
# ---------------------------
@'
from enum import Enum

class UserRole(str, Enum):
    datore = "datore"
    revisore = "revisore"
    rspp = "RSPP"
    lavoratore = "lavoratore"
'@ | Set-Content "$proj\app\config\roles.py" -Encoding UTF8

# ---------------------------
# FILE: templates/index.html
# ---------------------------
@'
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ translations.title }}</title>
</head>
<body>
    <h1>{{ translations.welcome }}</h1>

    <p>{{ translations.active_role }}: {{ role }}</p>

    <div>
        <h3>{{ translations.change_language }}</h3>
        <a href="/?lang=it&role={{ role }}">IT</a> |
        <a href="/?lang=en&role={{ role }}">EN</a> |
        <a href="/?lang=fr&role={{ role }}">FR</a> |
        <a href="/?lang=de&role={{ role }}">DE</a>
    </div>

    <div>
        <h3>{{ translations.select_role }}</h3>
        <a href="/?lang={{ lang }}&role=datore">Datore</a> |
        <a href="/?lang={{ lang }}&role=revisore">Revisore</a> |
        <a href="/?lang={{ lang }}&role=RSPP">RSPP</a> |
        <a href="/?lang={{ lang }}&role=lavoratore">Lavoratore</a>
    </div>
</body>
</html>
'@ | Set-Content "$proj\templates\index.html" -Encoding UTF8

# ---------------------------
# FILES: locales/*.json
# ---------------------------
$translations = @{
    "it" = '{"title":"Benvenuto","welcome":"Benvenuto nell\'applicazione TPI evoluto!","change_language":"Cambia lingua","active_role":"Ruolo attivo","select_role":"Seleziona ruolo"}'
    "en" = '{"title":"Welcome","welcome":"Welcome to the TPI evoluto application!","change_language":"Change language","active_role":"Active role","select_role":"Select role"}'
    "fr" = '{"title":"Bienvenue","welcome":"Bienvenue sur l\'application TPI evoluto!","change_language":"Changer de langue","active_role":"Rôle actif","select_role":"Sélectionner le rôle"}'
    "de" = '{"title":"Willkommen","welcome":"Willkommen zur TPI evoluto Anwendung!","change_language":"Sprache wechseln","active_role":"Aktive Rolle","select_role":"Rolle auswählen"}'
}

foreach ($lang in $translations.Keys) {
    $path = "$proj\locales\$lang.json"
    $translations[$lang] | Set-Content $path -Encoding UTF8
    Write-Host "Creato file: $path"
}

Write-Host "=== I18N + Ruoli pronti! ===" -ForegroundColor Green
