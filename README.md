# TPI_evoluto — Orchestratore DPI (FastAPI)

Backend FastAPI per gestione DPI via CSV: template, import/export, catalogo, metriche e report HTML.
Obiettivo: pipeline stabile e ripetibile per classificazione, import massivo e log.

## API principali (CSV/DPI)
Base URL (dev): `http://127.0.0.1:8012`

- `GET  /api/dpi/csv/template`
- `POST /api/dpi/csv/save`
- `GET  /api/dpi/csv/catalogo`
- `GET  /api/dpi/csv/export`
- `POST /api/dpi/csv/import-file`
- `POST /api/dpi/csv/import`
- `GET  /api/dpi/csv/metrics`
- `GET  /api/dpi/csv/report.html`
- `GET  /openapi.json`

## Cataloghi
- `E:\CLONAZIONE\tpi_evoluto\app\data\catalog_linee_vita.json`
- `E:\CLONAZIONE\tpi_evoluto\app\data\catalog_inox.json`

## Avvio (Windows PowerShell)
```powershell
cd E:\CLONAZIONE\tpi_evoluto
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8012 --log-level warning
