# TPI_evoluto
![CI](https://github.com/aicreator76/TPI_evoluto/actions/workflows/ci.yml/badge.svg)

## TPI / AELIS â€“ Dashboard & Agenti (#7 Operativo, #8 Ordini DPI)
Questo repository ospita la dashboard TPI e lâ€™integrazione con gli agenti AELIS:
- **Agente #7 â€“ Operativo Dashboard:** notifica scadenze DPI, badge, KPI.
- **Agente #8 â€“ Ordini DPI:** crea/chiude ordini di sostituzione DPI (work orders).

---

## API

### `/health` (GET)
- **200** â†’ `{"status":"ok"}`

### `/api/dpi/csv/template` (GET, HEAD)
- Genera CSV â€œsicuroâ€ per Excel/Windows con **BOM UTF-8** e terminazioni **CRLF**.
- **Header**:
  - `Content-Type: text/csv; charset=utf-8`
  - `Content-Disposition: attachment; filename="dpi_template.csv"`
  - `Cache-Control: no-store`

### `/api/dpi/csv/import` (POST multipart/form-data)
- Campo richiesto: `file` (CSV).
- **Limite**: 5 MB.
- **Validazioni**:
  - Presenza intestazione:  
    `codice,descrizione,marca,modello,matricola,assegnato_a,data_inizio,data_fine,certificazione,scadenza,note`
  - Ignora BOM e line endings misti.
- **Audit**: salva il file grezzo in `data/imports/` con timestamp.
- **200** â†’ `{"status":"ok","rows":<num_righe_valide>}`
- **Dipendenza**: `python-multipart`.

---

## Test rapidi (curl)

> Sostituisci `{PORT}` con la porta in uso (es. **8011**).

```bash
# Health
curl -sS http://127.0.0.1:{PORT}/health

# Template (ispeziona header)
curl -i  http://127.0.0.1:{PORT}/api/dpi/csv/template

# Scarica il template
curl -fS http://127.0.0.1:{PORT}/api/dpi/csv/template -o dpi_template.csv

# Import (usa un CSV reale)
curl -sS -F "file=@dpi_template.csv" http://127.0.0.1:{PORT}/api/dpi/csv/import

[![CI](https://github.com/aicreator76/TPI_evoluto/actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
[![Docs](https://github.com/aicreator76/TPI_evoluto/actions/workflows/docs.yml/badge.svg)](../../actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

<!-- AELIS: CSV API BADGE START -->
[![CSV API](https://img.shields.io/badge/CSV%20API-ready-brightgreen?style=flat-square)](docs/http/api-tests.http)
<<<<<<< HEAD
[![Endpoints](https://img.shields.io/badge/Endpoints-9-blue?style=flat-square)](docs/http/api-tests.http)

**Endpoints pronti**  
`GET /api/dpi/csv/template` · `POST /api/dpi/csv/save` · `GET /api/dpi/csv/catalogo` · `GET /api/dpi/csv/export?gruppo=...&columns=...` · `POST /api/dpi/csv/import-file` · `GET /api/dpi/csv/metrics` · `GET /healthz` · `GET /version` · `GET /metrics` · `POST /api/dpi/csv/import-file`
=======
[![Endpoints](https://img.shields.io/badge/Endpoints-9-blue?style=flat-square)](docs/http/api-tests.http)

**Endpoints pronti**  
`GET /api/dpi/csv/template` · `POST /api/dpi/csv/save` · `GET /api/dpi/csv/catalogo` · `GET /api/dpi/csv/export?gruppo=...&columns=...` · `POST /api/dpi/csv/import-file` · `GET /api/dpi/csv/metrics` · `GET /healthz` · `GET /version` · `GET /metrics`
>>>>>>> site/nov-2025-polish

➡️ Prove rapide: [docs/http/api-tests.http](docs/http/api-tests.http)
<!-- AELIS: CSV API BADGE END -->

<<<<<<< HEAD

=======
>>>>>>> site/nov-2025-polish


