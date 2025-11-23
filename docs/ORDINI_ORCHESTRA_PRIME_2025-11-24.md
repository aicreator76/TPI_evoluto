# ORDINI ORCHESTRA-PRIME – 2025-11-24

Fronte principale di giornata:
**Portare a casa i PR del Catalogo DPI e rendere visibile il cambiamento sui docs.**

---

## COMPITO 1 – PR DOCS ? MAIN (#63)

Obiettivo: chiudere la PR **#63 – docs: refresh tema Material e homepage TPI_evoluto**.

- [ ] Aprire STATO-REGNO e verificare che il branch `docs/theme-refresh` sia aggiornato.
- [ ] Da GitHub: rivedere PR #63 (solo file docs/mkdocs).
- [ ] Risolvere eventuali conflitti (es. `README.md`) in locale e pushare.
- [ ] Quando i check sono verdi, fare **Merge** verso `main`.

Misura di successo:
- PR #63 chiusa come *merged*.
- Site docs su `https://aicreator76.github.io/TPI_evoluto/` con nuova homepage + sezione Catalogo.

---

## COMPITO 2 – PR BACKEND CATALOGO DPI (#64)

Obiettivo: portare avanti la PR **#64 – feat: Catalogo DPI API e whitelist rate limit** fino a “quasi merge”.

- [ ] Da GitHub: controllare PR #64 (descrizione e checklist già presenti).
- [ ] In locale: `git checkout feat/catalogo-dpi-api` + `git pull`.
- [ ] Lanciare:
  - `uvicorn app.main:app --reload --port 8011`
  - `.\scripts\CESARE\smoke_catalogo_DPI_2025-11-20.ps1`
- [ ] Aggiornare la checklist PR #64:
  - [x] CI verde
  - [x] Smoke Catalogo DPI ok
  - [x] Nessun file `data/cataloghi/...` nel diff

Misura di successo:
- PR #64 con checklist tutta spuntata.
- Nessun file runtime nel diff.
- Commento finale sul PR con esito dello smoke.

---

## COMPITO 3 – LIFTING VISIVO MKDOCS

Obiettivo: rendere i docs **belli a schermo**, non solo corretti.

Branch di lavoro: `docs/theme-refresh`.

- [ ] In `mkdocs.yml` impostare palette Material (primary/accent, dark mode se vuoi).
- [ ] Abilitare features utili:
  - `navigation.tabs`
  - `navigation.sections`
  - `search.highlight`, `search.suggest`
- [ ] Verificare in `mkdocs serve` che:
  - Home sia “TPI_evoluto – Orchestratore DPI & Impianti”
  - Sezione “Catalogo DPI” sia ben visibile nella nav.
- [ ] Commit:
  - `git add mkdocs.yml docs/index.md docs/catalogo/index.md`
  - `git commit -m "Docs: palette Material e nav Catalogo migliorata"`
  - `git push`

Misura di successo:
- Docs locali con look più moderno e leggibile.
- PR #63 aggiornata automaticamente con il lifting.

---

## NOTE TECNICHE (per la Regina)

- Branch attivi oggi:
  - `docs/theme-refresh` ? PR #63 (docs / tema)
  - `feat/catalogo-dpi-api` ? PR #64 (backend Catalogo DPI)
- Script delta giornaliero: `E:\CLONAZIONE\scripts\CESARE\genera_delta_giornaliero.ps1`
- Prima di iniziare i lavori:
  - Eseguire `STATO-REGNO`
  - Fare `git fetch --all` e `git pull` sui branch interessati.
