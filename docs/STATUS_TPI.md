# Stato TPI (generale) – dicembre 2025

## Dove siamo oggi

- **Backend**: FastAPI + SQLAlchemy + Alembic avviabile in dev con `TPI_SERVER_DEV`.
- **Schema DB TPI v1** definito e documentato in `Schema TPI v1`.
- **Catalogo DPI**: router CSV collegati (`template`, `save`, `catalogo`, `export`, `import-file`, `import`).
- **Modulo DPI – Agente 0**: cruscotto HTML/JSON funzionante con warning 30gg e feed verso n8n.
- **Documentazione backend**: pagine attive
  - `Stato Backend`
  - `Cruscotto CESARI/Agenti`
  - `Schema DB TPI v1`.

## Cosa è pronto per la demo in ufficio

- Colleghe/i possono:
  - vedere API su `http://127.0.0.1:8000/docs`;
  - aprire la doc backend su `http://127.0.0.1:8001`;
  - vedere il cruscotto DPI locale (`public\agente0_dashboard.html`).
- Snapshot Git esistente per il modulo DPI: `tpi-SNAPSHOT-DPI-2025-11-30`.

## Backlog breve (prossimi step)

1. Stabilizzare migrazioni Alembic (header, metadata, enums allineati).
2. Introdurre session factory centralizzata (`SessionLocal` + `get_db`).
3. Rafforzare Auth JWT (SECRET da env, hashing password, ruoli/tenant).
4. Scrivere test Pytest minimi (import app, `/health`, Alembic upgrade).

## Backlog medio

- Attivare CI completa (lint + test + Alembic check).
- Collegare cruscotto CESARI ai log reali di Agente 0 e alle metriche CI.
- Preparare tag ufficiale **tpi-DEMO-REGINA-YYYY-MM-DD** per ogni demo importante.
