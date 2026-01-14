# 33 – Endpoint VETRINA per demo TPI (TPI_evoluto + TPI_api_staging)
Data: 2025-12-10

Obiettivo:
- avere un set di endpoint coerente tra TPI_evoluto e TPI_api_staging
- dare da SUBITO la sensazione di:
  - motore AI (maggiordomo / orchestratore),
  - DPI seri (con revisioni),
  - funi in fibra / forestale,
  - sottogancio,
  - accessori giÃƒ  strutturati.

> NOTA: i path qui sotto sono da allineare ai nomi REALI presenti in
> `32_mappa_endpoint_TPI_vs_STAGING_2025-12-10.md` e nel codice.
> Questo file è la REGIA, non il codice.

------------------------------------------------------------
1) AI / MAGGIORDOMO / ORCHESTRATORE
------------------------------------------------------------

Endpoint desiderati (nomi da agganciare a quelli reali):

- [ ] `GET  /api/magister/overview`
      Scopo: messaggio chiaro che spiega:
      - che cos'è l'orchestratore AI TPI
      - quali aree gestisce (DPI, funi, accessori, forestale...)
      - che questa API è un "maggiordomo" per i CESARI/Regine.

- [ ] `GET  /api/magister/health`
      Scopo: health specifico del livello "maggiordomo".

------------------------------------------------------------
2) DPI + REVISIONI
------------------------------------------------------------

Endpoint desiderati (agganciare alla mappa reale):

- [ ] `GET  /api/dpi/overview`
      Scopo: numeri chiave DPI (totale DPI, in uso, scaduti, in revisione...).

- [ ] `GET  /api/dpi/listino`
      Scopo: elenco DPI con paginazione (limit/offset).

- [ ] `GET  /api/dpi/{id}`
      Scopo: dettaglio DPI singolo (campi principali).

- [ ] `GET  /api/dpi/{id}/revisioni`
      Scopo: elenco revisioni fatte (anche solo lettura, demo-ready).

------------------------------------------------------------
3) FUNI IN FIBRA – FORESTALE
------------------------------------------------------------

Endpoint desiderati:

- [ ] `GET  /api/funi-fibra/overview`
      Scopo: panoramica funi in fibra (magari con focus FORESTALE).

- [ ] `GET  /api/funi-fibra/listino`
      Scopo: listino funi in fibra con filtri base (es. famiglia, portata).

- [ ] `GET  /api/funi-fibra/{id}`
      Scopo: dettaglio prodotto (per una demo concreta).

- [ ] (Opzionale) `GET  /api/funi-fibra/forestale/highlight`
      Scopo: 2–3 articoli "bandiera" per il settore forestale.

------------------------------------------------------------
4) SOTTOGANCIO
------------------------------------------------------------

Endpoint desiderati:

- [ ] `GET  /api/sottogancio/overview`
      Scopo: numeri chiave sottogancio / movimenti.

- [ ] `GET  /api/sottogancio/listino`
      Scopo: elenco soluzioni sottogancio (demo-friendly).

------------------------------------------------------------
5) ACCESSORI – MODELLO DI RIFERIMENTO
------------------------------------------------------------

Endpoint giÃƒ  attivi in TPI_evoluto (da UP-livellare su STAGING):

- [ ] `GET  /api/accessori/overview`
- [ ] `GET  /api/accessori/listino`
- [ ] `GET  /api/accessori/listino/filtrato`
- [ ] `GET  /api/accessori/listino/by-code/{codice}`
- [ ] `GET  /api/accessori/listino/export`
      Scopo: mostrare come TPI gestisce un listino completo + export CSV.

------------------------------------------------------------
6) HEALTH / META / VERSIONE
------------------------------------------------------------

Endpoint base da verificare/allineare:

- [ ] `GET  /health`   o `/healthz`
      Scopo: ping semplice API.

- [ ] `GET  /version`
      Scopo: versione TPI_evoluto / API staging (anche solo stringa).

- [ ] (Opzionale) `GET  /meta`
      Scopo: sintetizzare:
      - nome progetto,
      - ambiente (staging),
      - elenco macro-aree attive (DPI, funi, accessori, ecc.).

------------------------------------------------------------
7) NOTE DI LAVORO
------------------------------------------------------------

- Passo 1:
  - Aprire `32_mappa_endpoint_TPI_vs_STAGING_2025-12-10.md`.
  - Per ogni sezione qui sopra:
    - agganciare ciascun endpoint al path reale,
    - segnare se esiste in:
      - TPI_evoluto
      - TPI_api_staging
      - entrambi.

- Passo 2:
  - Per gli endpoint mancanti in STAGING:
    - o li semplifichiamo (mock),
    - o ne scegliamo 1–2 per area come "must-have" per la demo.

- Passo 3:
  - Aggiornare README di:
    - `E:\CLONAZIONE\tpi_evoluto`
    - `E:\CLONAZIONE\TPI_api_staging`
  - Inserire tabella riassuntiva con questi endpoint vetrina.

Questo file è la GUIDA UFFICIALE per parlare delle API lunedì:
non solo "funziona", ma "si capisce cosa fa il Regno".
