# TPI Evoluto — Enterprise Scadenze DPI (FastAPI)

TPI Evoluto genera **eventi di scadenza** in modo **deduplicato** e **idempotente**.
Stati ufficiali: **pending** (da gestire) e **ack** (gestito).
Nessun “sent” finto: flusso **auditabile**, coerente, enterprise.

## Live
- Render OpenAPI: https://tpi-evoluto-staging.onrender.com/openapi.json
- GitHub Pages (docs): INSERISCI_URL_PAGES

## Release pronte
- Cataloghi Enterprise: https://github.com/aicreator76/TPI_evoluto/releases/tag/cataloghi-enterprise-2026-01-11

## Cosa risolve
- Scadenze gestite a mano (Excel/email) con rischio non conformità
- Nessuna traccia di presa in carico
- Dati incoerenti tra reparti e sedi

## Come funziona (vero, senza magie)
- Il backend genera eventi e li registra (deduplica, idempotenza)
- Gli utenti prendono in carico e chiudono con ACK
- KPI e report: pending, ack, overdue, stale (roadmap)

## Demo 5 minuti
1) OpenAPI
- GET /openapi.json

2) Template CSV
- GET /api/dpi/csv/template

3) Import CSV
- POST /api/dpi/csv/import

4) Eventi (orchestrator)
- GET /events?tenant=ACME
- POST /events/id/ack

## Enterprise: SAP + CRM (adapter ready)
Pattern consigliato: Connector/Adapter pluggabile
- pull_events
- push_ack
- sync_assets
- healthcheck
Tutto correlato con sync_run_id + external_id.

## UI enterprise (proposta)
- Next.js + Tailwind + shadcn/ui + Recharts
- DataTable filtri tenant/status/date
- Bulk actions + export CSV
- Audit log per sync_run_id

## CI
- pre-commit, mypy, compileall, pip-audit
- smoke-api workflow: boot + template + import
