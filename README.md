# TPI_evoluto
![CI](https://github.com/aicreator76/TPI_evoluto/actions/workflows/ci.yml/badge.svg)

## TPI / AELIS Ã¢â‚¬â€œ Dashboard & Agenti (#7 Operativo, #8 Ordini DPI)
Questo repository ospita la dashboard TPI e lÃ¢â‚¬â„¢integrazione con gli agenti AELIS:
- **Agente #7 Ã¢â‚¬â€œ Operativo Dashboard:** notifica scadenze DPI, badge, KPI.
- **Agente #8 Ã¢â‚¬â€œ Ordini DPI:** crea/chiude ordini di sostituzione DPI (work orders).

---

## API

### `/health` (GET)
- **200** Ã¢â€ â€™ `{"status":"ok"}`

### `/api/dpi/csv/template` (GET, HEAD)
- Genera CSV Ã¢â‚¬Å“sicuroÃ¢â‚¬Â per Excel/Windows con **BOM UTF-8** e terminazioni **CRLF**.
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
- **200** Ã¢â€ â€™ `{"status":"ok","rows":<num_righe_valide>}`
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

[![CI](https://github.com/' + $REPO + '/actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
[![Docs](https://github.com/' + $REPO + '/actions/workflows/docs.yml/badge.svg)](../../actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

