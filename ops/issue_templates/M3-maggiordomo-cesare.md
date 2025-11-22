# M3 – Maggiordomo CESARE (console totale del Regno)

## Contesto

Voglio un maggiordomo digitale unico (CESARE) che:
- mostri la **Console del Sovrano** con comandi rapidi (RIPRENDI-REGNO, ORCHESTRA-PRIME, REGINA-AELIS, ecc.);
- apra automaticamente gli ambienti di lavoro (FastAPI, n8n, repo TPI_evoluto);
- faccia da cruscotto operativo per snapshot, release, log e stati dei CESARI/CESARONI.

## Obiettivi

- Un solo comando PowerShell da lanciare:
  - mostra la console ASCII di Camelot;
  - espone i comandi rapidi;
  - permette di lanciare script già esistenti (build, test, uvicorn, n8n, snapshot, ecc.).
- Documentare questi comandi in modo chiaro (README o wiki).

## Deliverable

- Script principale: `ops\CESARE_maggiordomo.ps1` (o nome equivalente) che:
  - mostra la console;
  - gestisce il menu comandi;
  - richiama gli altri script/sottocomandi.
- Documentazione:
  - sezione dedicata in README o doc interna: “Maggiordomo CESARE – Console del Sovrano”.
- Eventuale alias/shortcut per PowerShell.

## Requisiti tecnici

- Compatibile con Windows PowerShell / pwsh.
- Nessuna dipendenza “magica”: solo script nella repo (`ops\`, `scripts\`).
- Parametri base:
  - modalità “demo” (solo stampa comandi),
  - modalità “operativa” (esegue davvero script).

## Task

- [ ] Disegnare la struttura della console (schermata iniziale + menu).
- [ ] Mappare i comandi rapidi esistenti:
      - [ ] RIPRENDI-REGNO → cruscotto + stato TPI/snapshot
      - [ ] ORCHESTRA-PRIME → solo cruscotto tecnico
      - [ ] REGINA-AELIS → prompt dedicato per comandi di alto livello
      - [ ] STATO-REGNO → riepilogo rapido TPI/snapshot/release
- [ ] Definire un modulo di configurazione (es. `ops\config\console.json` o `.psd1`) per:
      - [ ] percorsi principali (E:\CLONAZIONE\..., repo, log, backup)
      - [ ] mapping comando → script PowerShell da lanciare.
- [ ] Implementare `ops\CESARE_maggiordomo.ps1`:
      - [ ] stampa banner Camelot
      - [ ] mostra elenco comandi
      - [ ] legge input utente
      - [ ] esegue lo script corrispondente.
- [ ] Integrare log minimo:
      - [ ] ogni comando eseguito viene registrato in `LOG\maggiordomo-YYYY-MM-DD.log`.
- [ ] Aggiornare documentazione (README o docs) con:
      - [ ] cosa fa il Maggiordomo
      - [ ] come si lancia
      - [ ] esempi di utilizzo.
- [ ] Aggiungere eventuali TODO per evoluzione futura (integrazione con CESARONI di rete/stampante).

## Note

- Questo Maggiordomo dovrà diventare il punto di ingresso **unico** per lavorare su TPI_evoluto.
- Gli altri script (build, test, uvicorn, snapshot) NON vengono riscritti, ma richiamati.
