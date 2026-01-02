# Cruscotto CESARI / Agenti

Cruscotto operativo per Sovrano, Regina e tecnici.

## Semafori rapidi

### Modulo DPI – Agente 0

- **Stato**: 🟢 / 🟡 / 🔴
- **Fonte**: `public\agente0_dashboard.html` + log `logs\agente0_dashboard.json`
- **Note**: numero DPI, warning, scaduti, ultimo run.

### Backend API TPI_evoluto

- **Stato**: 🟢 / 🟡 / 🔴
- **Check**:
  - `GET /healthz`
  - `GET /api/ops/version`

### Git / CI

- **Stato**: 🟢 / 🟡 / 🔴
- **Fonte**: git status, ultimo tag, esito CI.

---

## Riepilogo STATO (backend + DPI)

- Backend dev attivo con `TPI_SERVER_DEV`.
- Modulo DPI Agente 0 attivo con `run_agente0.ps1`.
- Doc tecnica aggiornata (Stato Backend + Schema DB).

---

## PROBLEMI aperti

- Migrazioni Alembic / metadata da consolidare.
- Session factory e auth da rafforzare.
- Test/CI minimi da attivare.

---

## MOSSE POWER

1. Stabilizzare backend (Alembic + sessioni).
2. Congelare demo DPI regale.
3. Accendere CI + tag `tpi-DEMO-REGINA-YYYY-MM-DD`.
