# === FIX_I18N_UI_AND_RUN.ps1 ===
Write-Host "=== Avvio script completo i18n + UI + test ===" -ForegroundColor Cyan
Set-Location "C:\TPI_evoluto"

# 1. Aggiorna i18n.py
@'
import os
import json
from fastapi import Request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOCALES_DIR = os.path.join(BASE_DIR, "locales")

SUPPORTED_LANGUAGES = ["it", "en", "fr", "de"]

def get_locale(request: Request):
    lang = request.query_params.get("lang", "it")
    if lang not in SUPPORTED_LANGUAGES:
        lang = "it"
    file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
    with open(file_path, encoding="utf-8") as f:
        return json.load(f), lang
'@ | Set-Content "app/config/i18n.py" -Encoding UTF8
FIX_I18N_UI_AND_RUN.ps1