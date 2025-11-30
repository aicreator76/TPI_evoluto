# Stato progetto TPI_evoluto – 2025-11-30

## 1. Panoramica

La piattaforma TPI_evoluto è in fase **core-dev**: le fondamenta tecniche ci sono, ma non è ancora “production ready”.
Molti moduli chiave (orchestratore, console operativa, integrazioni, multi-tenant, autenticazione, CRUD complete) sono **in sviluppo** o **non completati**.

### Cosa funziona oggi (snapshot)

- **Agente 0 – DPI**
  - Cruscotto HTML DPI funzionante (dashboard JSON → HTML).
  - Feed notifiche per n8n operativo (file JSON per integrazioni).
- **Catalogo DPI CSV**
  - Template CSV stabile.
  - Import/export CSV + JSON canonico del catalogo.
- **Strato documentazione**
  - Ordini ORCHESTRA-PRIME giornalieri.
  - Schema DB v1 documentato in `docs/db/schema_TPI_v1.md`.
  - `STATUS_TPI.md` come punto unico di verità sullo stato del progetto.

### Cosa è ancora WIP

- **Backend strutturale**
  - Schema DB definito ma non ancora migrato in Postgres.
  - Migrazioni Alembic da impostare e testare (`alembic init`, env, versioni).
  - Modelli SQLAlchemy da completare e collegare all’API FastAPI.

- **Sicurezza & multi-tenant**
  - Autenticazione (JWT/sessioni) da progettare/integrare.
  - Multi-tenant logico (campo `tenant_id` in tutte le tabelle/API) ancora da applicare.
  - Policy di segregazione dati e residenza (data residency) da definire.

- **Funzionalità applicative**
  - CRUD DPI / impianti / ispezioni / allegati.
  - Orchestratore 0 completo per scadenze DPI/impianti.
  - Console operativa (Maggiordomo CESARE) con comandi di controllo stato.
  - Hub integrazioni (webhook/eventi) per collegare TPI con sistemi esterni.

- **Repo & CI**
  - Pulizia repo e README “presentabile”.
  - Pipeline CI da stabilizzare (test, lint, migrazioni DB in pipeline).
  - Issue “help wanted” su orchestratore/CI ancora aperte.

---

## 2. Moduli principali – Stato rapido

| Modulo                         | Stato attuale        | Note POWER                                                  |
|--------------------------------|----------------------|-------------------------------------------------------------|
| DB schema (issue #48)          | **Definito (doc)**   | Schema v1 in `docs/db/schema_TPI_v1.md`. Da migrare in DB.  |
| Migrazioni Alembic (#49)       | **TODO**             | Struttura non ancora creata.                               |
| Autenticazione JWT (#50)       | **TODO**             | Bloccante per uso reale multi-utente.                      |
| Multi-tenant logico (#51, #57) | **TODO**             | `tenant_id` ovunque + policy separazione dati.             |
| CRUD DPI/Impianti (#52–54)     | **TODO**             | Dipendono da schema DB + Alembic.                          |
| Orchestratore 0 (#55)          | **PARZIALE**         | Agente 0 DPI lato cruscotto/alert attivo, resto da estendere. |
| Integrazione n8n (#61)         | **PARZIALE**         | Feed notifiche JSON ok, integrazione eventi da completare. |
| Enterprise Integration Hub (#58)| **TODO**            | Webhook/event bus da progettare.                           |
| Pulizia repo & README (#56)    | **TODO**             | README e struttura progetto da rendere leggibili.          |
| Console CESARE (#62)           | **TODO**             | Maggiordomo/console operativa ancora concettuale.          |

---

## 3. Rischi & blocchi

- Senza **schema DB + migrazioni Alembic**, nessuna CRUD reale può andare in produzione.
- Senza **autenticazione + multi-tenant**, il sistema non è sicuro né adatto a clienti multipli.
- Senza **repo pulita + README forte**, è difficile coinvolgere collaboratori o aprire il progetto.

---

## 4. Note operative per le prossime fasi (POWER)

1. **Chiudere issue #48 – Schema DB**
   - Mantieni `docs/db/schema_TPI_v1.md` come *sorgente di verità* del modello dati.
   - Allinea ogni futura migrazione Alembic a questo schema.

2. **Attivare Alembic (issue #49)**
   - Creare `app/db/base.py` e modelli SQLAlchemy coerenti con lo schema.
   - Inizializzare Alembic (`alembic init alembic`) e configurare `env.py` per usare `DATABASE_URL` e `app.db.base.Base`.

3. **Preparare autenticazione e multi-tenant (issue #50, #51, #57)**
   - Definire chiaramente modelli `utente`, `ruolo`, `azienda (tenant)`.
   - Imporre `tenant_id` come FK su tutte le entità applicative (DPI, impianti, ispezioni, ecc.).

4. **Stabilizzare CI e repo (issue #56)**
   - Aggiornare README con: stato, come avviare il server, come lanciare Alembic, come girano gli agenti.
   - Assicurarsi che pre-commit + test base passino su ogni push.

5. **Solo dopo: estendere orchestratore e integrazioni**
   - Ampliare Agente 0 per includere impianti + logiche cross-tenant.
   - Agganciare n8n, webhook e console CESARE per il controllo da “Regno”.

---

## 5. Sintesi per la Regina

- Il progetto è in **costruzione delle fondamenta**, non in rifinitura.
- Oggi funzionano già cruscotti DPI e cataloghi, ma DB, sicurezza e multi-tenant sono ancora da completare.
- Le prossime mosse decisive sono: **schema DB → migrazioni Alembic → sicurezza e multi-tenant → CRUD principali**.
