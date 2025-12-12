# 03 – MERGE PLAN OPERATIVO TPI_evoluto + TPI_api_staging

## Fase 0 – Preparazione (oggi)

- [x] Creare la cartella `docs/unificazione_tpi_api/` in TPI_evoluto.
- [x] Scrivere:
  - stato attuale,
  - scelte architetturali,
  - piano di merge.
- [ ] Confermare percorso locale di `TPI_api_staging`.
- [ ] Eseguire i comandi di diff definiti in `run_diff_unificazione.ps1`.

## Fase 1 – Allineamento endpoint critici (breve termine)

1. Definire elenco endpoint “vetrina” per la demo:
   - `/health` o `/healthz`,
   - `/version`,
   - 1–2 endpoint chiave (es. listino ACCESSORI, FUNI, LYNX).

2. Per ciascun endpoint:
   - confrontare la firma (metodo, path, query params, body),
   - confrontare il payload di risposta,
   - allineare TPI_api_staging allo stile TPI_evoluto.

3. Aggiornare:
   - test in TPI_evoluto,
   - eventuali test in TPI_api_staging,
   - README di TPI_api_staging con elenco endpoint garantiti.

## Fase 2 – Core condiviso (medio termine)

1. In TPI_evoluto:
   - creare modulo `app/core/` (o nome equivalente) con:
     - modelli Pydantic di dominio,
     - funzioni di accesso DB riusabili,
     - util comuni (logging, gestione errori).

2. In TPI_api_staging:
   - sostituire la logica duplicata con import dal core (git subtree/submodule o altra strategia decisa).

3. Scrivere documentazione:
   - `docs/unificazione_tpi_api/04_CORE_CONDIVISO.md`
   - schema di dipendenze tra progetti.

## Fase 3 – Pulizia e storytelling (demo / partner)

- Ripassare i README:
  - TPI_evoluto = “motore”.
  - TPI_api_staging = “vetrina staging”.
- Preparare uno schema architetturale (anche in ASCII / PlantUML) con:
  - utenti / CESARI / Regine,
  - API staging,
  - core TPI,
  - DB / viste,
  - automazioni (n8n, ecc.).

Questo piano è pensato per essere:
- realistico,
- eseguibile,
- presentabile entro la demo.
