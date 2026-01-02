# 01 – STATO ATTUALE TPI_evoluto vs TPI_api_staging (2025-12-10)

## Repos coinvolti

- **TPI_evoluto**
  - Percorso locale (proposto): `E:\CLONAZIONE\tpi_evoluto`
  - Ruolo: core funzionale (modelli, viste, script, logica business, API principali).
  - Tecnologia: FastAPI, SQL, script PowerShell, pipeline n8n, ecc.

- **TPI_api_staging**
  - Percorso locale (da confermare/adattare): `E:\CLONAZIONE\TPI_api_staging`
  - Ruolo: API leggera pubblicata su Render (staging).
  - Tecnologia: FastAPI semplificata, healthcheck, endpoint selezionati.

## Obiettivo dell’unificazione

- Evitare doppioni di logica tra i due progetti.
- Avere un **piano unico di versioning** per:
  - schema DB,
  - API pubbliche,
  - viste e listini (ACCESSORI, FUNI, LYNX, FORESTALE, ecc.).
- Rendere TPI_api_staging un “guscio di pubblicazione” allineato a TPI_evoluto.

## Rischi attuali

- Divergenza di:
  - nomi endpoint,
  - payload JSON,
  - tipi di risposta,
  - gestione errori e rate-limit.
- Modifiche fatte su un repo e non replicate nell’altro.
- Complessità nel raccontare il progetto a terzi (demo lunedì, investitori, partner).

Questo documento fotografa lo **stato mentale e strutturale** al 10/12/2025
e apre la strada al merge pianificato.
