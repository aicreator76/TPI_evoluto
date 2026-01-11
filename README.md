# TPI Evoluto — Enterprise Scadenze DPI

TPI Evoluto genera eventi di scadenza in modo deduplicato e idempotente.
Stati ufficiali: pending e ack.
Nessun invio automatico finto.
Tracciabile. Auditabile. Vendibile.

## Live
- Render OpenAPI: https://tpi-evoluto-staging.onrender.com/openapi.json
- Docs pubbliche: INSERISCI_URL_PAGES

## Release
- Cataloghi Enterprise: https://github.com/aicreator76/TPI_evoluto/releases/tag/cataloghi-enterprise-2026-01-11

## Cosa risolve
- Scadenze gestite a mano, rischio non conformità
- Nessuna traccia di presa in carico
- Dati incoerenti tra reparti e sedi

## Come funziona
- Backend FastAPI genera eventi e li registra con deduplica e idempotenza
- Gli utenti prendono in carico e chiudono con ACK
- KPI e report pronti per dashboard enterprise

## Demo rapida
1) OpenAPI
- GET /openapi.json

2) Template CSV
- GET /api/dpi/csv/template

3) Import CSV
- POST /api/dpi/csv/import

4) Eventi orchestrator
- GET /events?tenant=ACME
- POST /events/id/ack

## Enterprise: SAP + CRM
Pattern consigliato: adapter pluggabile
- pull_events
- push_ack
- sync_assets
- healthcheck

Tracciamento
- sync_run_id per correlazione end to end
- external_id per mapping SAP CRM

Sicurezza
- secrets solo in env e secret store
- tenant isolation obbligatoria

## UI Enterprise proposta
- Next.js + Tailwind + shadcn/ui + Recharts
- Tabelle con filtri tenant, status, date range
- Bulk actions, export CSV, audit log
