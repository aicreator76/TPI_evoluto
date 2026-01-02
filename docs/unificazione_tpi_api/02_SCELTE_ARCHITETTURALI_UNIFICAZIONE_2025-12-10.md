# 02 – SCELTE ARCHITETTURALI PER L’UNIFICAZIONE

## 1. Verità unica del dominio

- **TPI_evoluto** è la _fonte di verità_ per:
  - modelli di dominio (DPI, ACCESSORI, FUNI, LYNX, FORESTALE, ecc.),
  - viste SQL e script di ingest,
  - API interne usate dai CESARI/LYNX,
  - test automatici di coerenza (pytest, Ruff, Black, ecc.).

- **TPI_api_staging** ha il ruolo di:
  - interfaccia pubblica per Render (staging),
  - adattatore che espone solo gli endpoint autorizzati,
  - contenitore di configurazioni specifiche per l’ambiente Render.

## 2. Pattern di integrazione (fase 1 – breve termine)

Nel breve termine (entro la demo di lunedì):

- TPI_evoluto rimane il progetto principale.
- TPI_api_staging viene allineato manualmente sugli endpoint critici:
  - healthcheck,
  - version,
  - listino DPI/ACCESSORI che servono alla demo.

Il focus NON è ancora il packaging perfetto,
ma **coerenza funzionale** percepibile da chi prova l’API.

## 3. Pattern di integrazione (fase 2 – medio termine)

Proposta di evoluzione:

1. Estrarre un piccolo “core” riusabile da TPI_evoluto:
   - es. modulo `tpi_core` contenente:
     - modelli Pydantic condivisi (richieste/risposte),
     - funzioni di accesso al DB per listini e DPI,
     - gestione errori standard.

2. Rendere TPI_api_staging dipendente da questo core tramite:
   - git subtree / submodule,
   - oppure pacchetto locale installato in fase di build su Render.

3. Allineare la documentazione:
   - OpenAPI generata da TPI_evoluto come riferimento unico,
   - README chiaro su cosa può e non può fare l’API di staging.

## 4. Linee guida di design

- NO duplicazione di logica critica tra i due progetti.
- SI a:
  - modelli condivisi,
  - nomi endpoint coerenti,
  - gestione errori standard (es. 4xx/5xx allineati),
  - log strutturati con stessi campi minimi: `req_id`, `endpoint`, `esito`.

Queste scelte guidano tutte le modifiche successive.
