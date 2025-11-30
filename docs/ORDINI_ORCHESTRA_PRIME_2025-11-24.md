ORDINI ORCHESTRA-PRIME 2025-11-24
REPO PRINCIPALE: E:\CLONAZIONE\tpi_evoluto

MISSIONE:
Oggi lavori SOLO su:
- PR #63 (docs)
- PR #64 (backend Catalogo DPI)
- Lifting visivo MkDocs

Quando rispondi, usa sempre questo formato:
STATO: cosa hai appena fatto
PROSSIMA AZIONE: prossimo comando concreto
EVIDENZA: solo output importante (OK / errore / URL)

--------------------------------------------------
COMPITO 1 – PR DOCS ? MAIN (#63)

Obiettivo: PR #63 – docs: refresh tema Material e homepage TPI_evoluto in stato MERGED.

1) Stato iniziale
- Esegui:
  - cd E:\CLONAZIONE\tpi_evoluto
  - .\ops\CESARE_stato_regno.ps1
- Apri la PR #63:
  - https://github.com/aicreator76/TPI_evoluto/pull/63

2) Lavoro sui docs (branch docs/theme-refresh)
- Branch:
  - git checkout docs/theme-refresh
  - git pull
- File che puoi toccare:
  - E:\CLONAZIONE\tpi_evoluto\mkdocs.yml
  - E:\CLONAZIONE\tpi_evoluto\docs\index.md
  - E:\CLONAZIONE\tpi_evoluto\docs\catalogo\index.md

3) Commit e push
- git add mkdocs.yml docs\index.md docs\catalogo\index.md
- git commit -m "Docs: tema Material e Catalogo DPI"
- git push

4) Chiusura PR
- Quando i check sono verdi ? fai il Merge della PR #63 verso main.

RISULTATO ATTESO COMPITO 1:
- PR #63 in stato "merged"
- Site docs online aggiornato:
  - https://aicreator76.github.io/TPI_evoluto/

--------------------------------------------------
COMPITO 2 – PR BACKEND CATALOGO DPI (#64)

Obiettivo: PR #64 – feat: Catalogo DPI API e whitelist rate limit con checklist COMPLETA.

1) Setup backend
- Repo/branch:
  - cd E:\CLONAZIONE\tpi_evoluto
  - git checkout feat/catalogo-dpi-api
  - git pull
- Avvia API:
  - uvicorn app.main:app --reload --port 8011

2) Smoke Catalogo DPI
- Script:
  - E:\CLONAZIONE\scripts\CESARE\smoke_catalogo_DPI_2025-11-20.ps1
- Endpoint da verificare senza errori:
  - http://127.0.0.1:8011/health
  - http://127.0.0.1:8011/api/dpi/csv/template
  - http://127.0.0.1:8011/api/dpi/csv/import
  - http://127.0.0.1:8011/api/dpi/csv/save
  - http://127.0.0.1:8011/api/dpi/csv/catalogo

3) Controllo diff + checklist
- PR:
  - https://github.com/aicreator76/TPI_evoluto/pull/64
- Verifica che nel diff NON compaia nulla sotto:
  - data/cataloghi/...
- Aggiorna la checklist nella PR #64:
  - Smoke Catalogo DPI OK
  - Nessun file runtime data/cataloghi/... nel diff

RISULTATO ATTESO COMPITO 2:
- PR #64 con checklist completa
- Smoke Catalogo DPI eseguito e OK
- Nessun data\cataloghi\... nel diff GitHub

--------------------------------------------------
COMPITO 3 – LIFTING VISIVO MKDOCS

Obiettivo: docs belli a schermo, non solo corretti.

File coinvolti:
- Tema:
  - E:\CLONAZIONE\tpi_evoluto\mkdocs.yml
- Homepage:
  - E:\CLONAZIONE\tpi_evoluto\docs\index.md
- Catalogo:
  - E:\CLONAZIONE\tpi_evoluto\docs\catalogo\index.md

1) Anteprima locale
- cd E:\CLONAZIONE\tpi_evoluto
- mkdocs serve

2) Check visivo in browser
- Titolo principale:
  - "TPI_evoluto – Orchestratore DPI & Impianti"
- Menu:
  - voce "Catalogo DPI" presente
  - sezione Orchestratore / Agenti visibile e sensata

3) Commit lifting
- git add mkdocs.yml docs\index.md docs\catalogo\index.md
- git commit -m "Docs: palette Material e nav Catalogo migliorata"
- git push   # branch: docs/theme-refresh

RISULTATO ATTESO COMPITO 3:
- Documentazione locale con tema Material e navigazione chiara
- PR #63 aggiornata automaticamente con il lifting

--------------------------------------------------
RITUALE INIZIO GIORNATA

Prima di eseguire qualsiasi ordine:
- cd E:\CLONAZIONE\tpi_evoluto
- git fetch --all
- .\ops\CESARE_stato_regno.ps1

Oggi puoi toccare SOLO:
- PR #63 (docs)
- PR #64 (backend Catalogo DPI)
NESSUN nuovo branch, NESSUN’altra PR.
