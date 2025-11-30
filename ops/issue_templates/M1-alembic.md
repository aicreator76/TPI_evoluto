## Contesto
Per evolvere lo schema DB senza caos serve un sistema di migrazioni versionato (es. Alembic per SQLAlchemy).

## Obiettivo
Configurare Alembic (o strumento equivalente) per:
- inizializzare lo schema DB definito in M1
- permettere migrazioni incrementali in futuro

## Task
- [ ] Aggiungere dipendenze Alembic (o tool scelto) a `pyproject.toml`/`requirements`
- [ ] Configurare `alembic.ini` e cartella migrazioni (es. `backend/migrations`)
- [ ] Creare migrazione iniziale che genera tutte le tabelle TPI v1
- [ ] Documentare comando di upgrade/downgrade in `docs/db/migrazioni.md`

## Criteri di accettazione
- [ ] Un nuovo ambiente può essere inizializzato con `alembic upgrade head` (o equivalente)
- [ ] Le tabelle generate corrispondono allo schema definito in M1
- [ ] README o docs contengono la procedura per eseguire le migrazioni
