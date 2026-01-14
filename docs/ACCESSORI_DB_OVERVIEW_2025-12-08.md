# ACCESSORI 3.0 – Overview DB (TPI_evoluto) – 2025-12-08

> **Nota importante**
> Le colonne sotto sono basate sulla struttura dei CSV `accessori_*.csv`.
> Se nel DB i nomi differiscono, aggiornare questo file e lo script SQL delle VIEW.

---

## 1. Tabelle coinvolte

### 1.1 `tpi_accessori_famiglie` (€°Ë† 30 righe)

**Ruolo**
Tabella di riferimento per le famiglie di accessori (ancoraggi, morsetti, catene G8, Tycan, tiranti/brache, ecc.).

**Colonne (assunte)**

- `id` – INTEGER PK
- `famiglia` – TEXT
  Nome della famiglia (es. `MORSETTI PER FUNI`, `CATENE G8`, `TYCAN`)
- `categoria` – TEXT
  Macro-gruppo o categoria interna (es. `ACCESSORI CATENA G8`)
- `sorgente` – TEXT
  Etichetta sorgente (es. `MORSETTI`, `CATENA_G8`, `TYCAN`, `ANCORAGGI`)
- `note` – TEXT
- `origine_catalogo` – TEXT
  Riferimento al file/pagina catalogo origine.

---

### 1.2 `tpi_accessori_morsetti` (51 righe)

**Ruolo**
Codici di dettaglio per i morsetti (accessori per funi).

**Colonne (assunte)**

- `id` – INTEGER PK
- `id_tpi` – TEXT
  Codice interno TPI (univoco per il listino 3.0).
- `codice` – TEXT
  Codice di fabbrica / commerciale.
- `descrizione` – TEXT
- `famiglia` – TEXT
  Testo collegabile a `tpi_accessori_famiglie.famiglia`.
- `sorgente` – TEXT (valore atteso: `MORSETTI`)
- `wll` – TEXT (o valore numerico) – portata di lavoro.
- `note` – TEXT
- `pagina_catalogo` – INTEGER
- `origine_catalogo` – TEXT

---

### 1.3 `tpi_accessori_catena_g8` (56 righe)

**Ruolo**
Codici per accessori catena grado 8.

**Colonne (assunte)**

Stessa struttura logica di `tpi_accessori_morsetti`:

- `id` – INTEGER PK
- `id_tpi` – TEXT
- `codice` – TEXT
- `descrizione` – TEXT
- `famiglia` – TEXT
- `sorgente` – TEXT (valore atteso: `CATENA_G8`)
- `wll` – TEXT
- `note` – TEXT
- `pagina_catalogo` – INTEGER
- `origine_catalogo` – TEXT

---

### 1.4 `tpi_accessori_tycan` (29 righe)

**Ruolo**
Codici per catene Tycan (FCHLIFT + FCHLASH).

**Colonne (assunte)**

- `id` – INTEGER PK
- `id_tpi` – TEXT
- `codice` – TEXT
- `descrizione` – TEXT
- `famiglia` – TEXT
- `sorgente` – TEXT (valore atteso: `TYCAN`)
- `wll` – TEXT
- `note` – TEXT
- `pagina_catalogo` – INTEGER
- `origine_catalogo` – TEXT

---

## 2. Relazioni logiche

> **Importante:** non è detto che il DB contenga FOREIGN KEY esplicite.
> Le relazioni sotto sono **logiche**, da usare per VIEW e BI.

1. **Famiglia € € Codici**
   - `tpi_accessori_famiglie.famiglia`
     € € `tpi_accessori_* .famiglia`
   - usata per collegare metadati di famiglia con righe di dettaglio.

2. **Sorgente**
   - `tpi_accessori_* .sorgente` distingue i tre mondi:
     - `MORSETTI` € €™ `tpi_accessori_morsetti`
     - `CATENA_G8` € €™ `tpi_accessori_catena_g8`
     - `TYCAN` € €™ `tpi_accessori_tycan`

3. **id_tpi**
   - `id_tpi` previsto come chiave logica interna TPI per il listino 3.0.
   - Unico all‚¬„¢interno di ogni tabella codici.
   - Potenzialmente unico cross-tabella, se gestito così a monte.

---

## 3. IntegritÃƒ  & coerenza (osservazioni)

- **CardinalitÃƒ  attese**
  - Una famiglia (`tpi_accessori_famiglie`) € €™ N codici in una o più tabelle codici.
- **Coerenza sorgente**
  - `sorgente` dovrebbe essere coerente con il tipo di tabella:
    - `MORSETTI` solo in `tpi_accessori_morsetti`
    - `CATENA_G8` solo in `tpi_accessori_catena_g8`
    - `TYCAN` solo in `tpi_accessori_tycan`
- **Join futuro per view**
  - Il join principale sarÃƒ :
    - per famiglia: `famiglia` (TEXT)
    - per analisi interna: `id_tpi` (se usato in più tabelle o cluster).

---

## 4. TODO / Verifiche consigliate

1. Verificare con:

   ```sql
   PRAGMA table_info(tpi_accessori_famiglie);
   PRAGMA table_info(tpi_accessori_morsetti);
   PRAGMA table_info(tpi_accessori_catena_g8);
   PRAGMA table_info(tpi_accessori_tycan);
