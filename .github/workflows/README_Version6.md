# TPI_evoluto

[![CI](https://github.com/aicreator76/TPI_evoluto/actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
[![Docs](https://github.com/aicreator76/TPI_evoluto/actions/workflows/docs.yml/badge.svg)](../../actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## TPI / AELIS – Dashboard & Agenti (#7 Operativo, #8 Ordini DPI)

Questo repository ospita la dashboard TPI e l’integrazione con gli agenti AELIS:

- **Agente #7 – Operativo Dashboard**: notifica scadenze DPI, badge, KPI.
- **Agente #8 – Ordini DPI**: crea/chiude ordini di sostituzione DPI (work orders).

---

## Docs e risorse rapide

- Docs Pages: <https://aicreator76.github.io/TPI_evoluto/>
- Catalogo DPI:
  - Overview: `docs/catalogo/index.md`
  - Checklist Go Live: `docs/catalogo/checklist_go_live.md`
  - Endpoint HTTP: `docs/http/catalogo_endpoints.md`
  - README Catalogo: `docs/catalogo/README.md`
- Prove rapide HTTP: `docs/http/api-tests.http`

---

## API principali

### `GET /health`

- `200` → `{"status":"ok"}`

### `GET, HEAD /api/dpi/csv/template`

Genera un CSV “sicuro” per Excel/Windows con BOM UTF-8 e terminazioni CRLF.

Header principali:

- `Content-Type: text/csv; charset=utf-8`
- `Content-Disposition: attachment; filename="dpi_template.csv"`
- `Cache-Control: no-store`

### `POST /api/dpi/csv/import` (multipart/form-data)

- Campo richiesto: `file` (CSV)
- Limite: **5 MB**

Validazioni:

- Presenza intestazione esatta:

  ```text
  codice,descrizione,marca,modello,matricola,assegnato_a,data_inizio,data_fine,certificazione,scadenza,note
