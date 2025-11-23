# Cruscotto COMPITI-REGINA – 2025-11-23

## Semaforo Unità
- 001–BLD (Catalogo / Smoke): 🟡 – Smoke arriva fino a /export, bloccato dal rate limit (429) in main.py
- 002–GIT (Docs / PR): 🟢 – Nav Catalogo + Canale operativo Camelot pronti su branch docs/theme-refresh
- 003–LMB (Testi & Grafica): 🔴 – Da completare (homepage + doc Catalogo)

## Esito giornata
- Smoke Catalogo: FALLITO solo su step 6 (429 Too Many Requests → 500), log salvato.
- Docs nav Catalogo/Orchestratore: aggiornati e pushati su docs/theme-refresh.
- Homepage + doc Catalogo: ancora da rifinire in ottica “prodotto”.

## TODO POWER prossima sessione
1. Valutare soglia/strategia rate limit in `app.main.dispatch` per smoke interno.
2. Rifinire `docs/index.md` con i 3 blocchi (per chi è / cosa fa oggi / cosa arriva dopo).
3. Scrivere doc Catalogo (percorsi reali + script CESARE + curl 8011) leggibile anche per commerciale.
