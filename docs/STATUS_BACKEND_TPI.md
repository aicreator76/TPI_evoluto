# STATUS BACKEND TPI_evoluto (POWER)

## STATO
- Backend FastAPI + SQLAlchemy + Alembic avviabile in dev.
- Schema DB v1 definito (docs + migrazione iniziale).
- Auth JWT abbozzata, router CSV/NFC/OPS presenti come base.
- Script `scripts/run_tpi_dev.ps1` avvia server + Alembic.

## PROBLEMI / RISCHI
- Migrazione Alembic iniziale fragile (BOM/header, metadata).
- Nessuna session factory centralizzata € €™ rischio leak/non thread-safe.
- Enums e modelli non ancora pienamente allineati.
- Gestione JWT/SECRET e hashing password da completare.
- Zero test/CI € €™ regressioni non intercettate.

## PRIORITÃƒ‚¬ PROSSIMI COMMIT
1. Sistemare definitivamente migrazione Alembic + `env.py` (metadata, DATABASE_URL).
2. Introdurre `app/db/base.py` con `naming_convention` + `app/db/session.py` con `SessionLocal`/`get_db`.
3. Stabilizzare router (`app.routers.*` assoluti) e centralizzare enums.
4. Rafforzare auth: `JWT_SECRET_KEY` da env, hashing con passlib, ruoli/tenant nei token.
5. Aggiungere test Pytest minimi (import app, `/health`, Alembic upgrade) e pipeline CI semplice.

## NOTE SICUREZZA (FOCUS)
- **JWT**: nessun secret hardcoded in prod; exp breve, rotazione programmata.
- **Password**: solo hash (bcrypt/argon2), mai testo in chiaro nei log.
- **Multi-tenant**: uso sistematico di `azienda_id` nei filtri.
- **CORS & rate limit**: origini limitate in prod, protezione login da brute-force.
- **Principio minimo privilegio**: utente DB applicativo senza permessi amministrativi.

_Sintesi: base solida, ma da stabilizzare subito Alembic + sessioni + auth. Poi test/CI._
