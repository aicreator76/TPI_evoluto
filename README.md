# TPI_evoluto
![CI](https://github.com/aicreator76/TPI_evoluto/actions/workflows/ci.yml/badge.svg)
[![Pages](https://github.com/aicreator76/TPI_evoluto/actions/workflows/pages.yml/badge.svg)](https://aicreator76.github.io/TPI_evoluto/)
[![Security](https://github.com/aicreator76/TPI_evoluto/actions/workflows/security.yml/badge.svg)](../../actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## TPI / AELIS – Dashboard & Agenti (#7 Operativo, #8 Ordini DPI)
Questo repository ospita la dashboard TPI e l'integrazione con gli agenti AELIS:
- **Agente #7 – Operativo Dashboard:** notifica scadenze DPI, badge, KPI.
- **Agente #8 – Ordini DPI:** crea/chiude ordini di sostituzione DPI (work orders).

---

## 🚀 Catalogo DPI – Go Live

Sistema completo di gestione catalogo DPI con API REST e dashboard HTML.

### Link rapidi

📚 **Documentazione**:
- [📖 Sito documentazione](https://aicreator76.github.io/TPI_evoluto/) – GitHub Pages
- [📋 Overview Catalogo](https://aicreator76.github.io/TPI_evoluto/catalogo/) – Guida completa
- [🔌 API Endpoints](https://aicreator76.github.io/TPI_evoluto/http/catalogo_endpoints/) – Documentazione REST
- [✅ Go Live Checklist](https://aicreator76.github.io/TPI_evoluto/catalogo/checklist_go_live/) – Verifiche pre-produzione

🧪 **Test e Prove**:
- [HTTP Tests](docs/http/api-tests.http) – Collezione test VS Code REST Client
- Smoke tests: `pytest tests/test_smoke.py`

### Endpoints API disponibili

[![CSV API](https://img.shields.io/badge/CSV%20API-ready-brightgreen?style=flat-square)](docs/http/api-tests.http)
[![Endpoints](https://img.shields.io/badge/Endpoints-11-blue?style=flat-square)](docs/http/catalogo_endpoints.md)

**Router CSV**: `/api/dpi/csv/`

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/template` | GET | Scarica template CSV |
| `/save` | POST | Import CSV raw (text/csv) |
| `/import-file` | POST | Upload CSV (multipart) |
| `/catalogo` | GET | Ritorna catalogo JSON |
| `/export` | GET | Export CSV filtrato |
| `/metrics` | GET | Metriche aggregate |
| `/report.html` | GET | Dashboard HTML |

**Endpoint meta** (root):
- `GET /healthz` – Health check
- `GET /version` – Versione app
- `GET /metrics` – Metriche globali

---

## Test rapidi

> Sostituisci `{PORT}` con la porta in uso (es. **8000** o **8011**).

### PowerShell

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/healthz"

# Visualizza metriche catalogo
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/metrics"

# Scarica template CSV
Invoke-WebRequest -Uri "http://localhost:8000/api/dpi/csv/template" -OutFile "template.csv"

# Upload CSV
$form = @{file = Get-Item -Path "catalogo.csv"}
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/import-file" -Method Post -Form $form

# Apri report HTML
Start-Process "http://localhost:8000/api/dpi/csv/report.html"

# Export filtrato
Invoke-WebRequest -Uri "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA&columns=listino" -OutFile "export.csv"
```

### curl

```bash
# Health check
curl http://localhost:8000/healthz

# Visualizza metriche
curl http://localhost:8000/api/dpi/csv/metrics | jq

# Scarica template
curl -o template.csv http://localhost:8000/api/dpi/csv/template

# Upload CSV
curl -F "file=@catalogo.csv" http://localhost:8000/api/dpi/csv/import-file

# Export filtrato
curl "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA" -o export.csv
```

---

## Sviluppo locale

### Prerequisiti
- Python 3.10 o 3.11
- pip

### Setup

```bash
# Installa dipendenze
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Avvia server locale
uvicorn app.main:app --reload --port 8000
```

### Test

```bash
# Smoke tests
pytest tests/test_smoke.py -v

# Coverage
pytest --cov=app --cov-report=html

# Pre-commit checks
pre-commit run --all-files
```

### Build docs

```bash
# Installa dipendenze docs
pip install -r requirements-docs.txt

# Build locale
mkdocs serve

# Build per deployment
mkdocs build
```

---

## CI/CD

Workflows configurati:
- **CI** (`.github/workflows/ci.yml`) – Lint, typecheck, tests
- **Security** (`.github/workflows/security.yml`) – pip-audit, bandit, semgrep
- **Pages** (`.github/workflows/pages.yml`) – Deploy MkDocs su GitHub Pages

Tutti i workflow sono verdi su branch:
- `main`
- `feat/catalogo-save`
- `copilot/fix-workflows-and-documentation`

---

## Licenza

MIT License – vedi [LICENSE](LICENSE)

---

## Link utili

- [Roadmap](https://aicreator76.github.io/TPI_evoluto/roadmap/)
- [Accessibilità](https://aicreator76.github.io/TPI_evoluto/ACCESSIBILITY/)
- [Aiuto](https://aicreator76.github.io/TPI_evoluto/HELP/)
- [Security Policy](SECURITY.md)
