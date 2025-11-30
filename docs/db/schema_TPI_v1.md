# Schema Database TPI_evoluto (v1)

Questo documento descrive lo **schema base Postgres** per TPI_evoluto.

Obiettivo: dare una base solida per:
- multi-tenant logico (per azienda/cliente)
- tracciamento DPI / impianti / ispezioni / allegati
- gestione operatori, corsi e attestati
- orchestratori e cruscotti di scadenza

---

## 1. Entità principali

### 1.1 `azienda` (tenant)
- `id` (PK)
- `nome`
- `partita_iva`
- `slug` / `codice`
- metadati vari (indirizzo, note, ecc.)

> Tutte le altre tabelle “di dominio” puntano a `azienda`.

---

### 1.2 `utente`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `email`
- `password_hash`
- `ruolo` (es. `ADMIN`, `HSE`, `DATORE`, `OPERATORE`, …)
- `attivo` (bool)

> Serve per autenticazione e ruoli applicativi.

---

### 1.3 `operatore`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `nome`
- `cognome`
- eventuale collegamento a `utente_id` (FK, opzionale)

> Rappresenta la persona fisica che usa DPI, partecipa ai corsi, ecc.

---

### 1.4 `dpi`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `codice`
- `descrizione`
- `categoria`
- `stato` (es. `OK`, `WARNING`, `SCADUTO`, `FUORI_SERVIZIO`)
- `data_scadenza`
- `operatore_id` (FK → `operatore.id`, opzionale, per DPI assegnati)

---

### 1.5 `impianto_anticaduta`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `codice`
- `descrizione`
- `ubicazione`
- `stato`
- `data_scadenza`

---

### 1.6 `ispezione`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `tipo_target` (`DPI` | `IMPIANTO`)
- `dpi_id` (FK → `dpi.id`, opzionale)
- `impianto_id` (FK → `impianto_anticaduta.id`, opzionale)
- `data_ispezione`
- `esito` (es. `OK`, `NON_CONFORME`, `DA_VERIFICARE`)
- `note`
- `operatore_id` (FK → `operatore.id`, opzionale)

---

### 1.7 `allegato`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `ispezione_id` (FK → `ispezione.id`)
- `tipo` (es. `FOTO`, `PDF`, `VIDEO`)
- `file_path`
- `created_at`

---

### 1.8 `corso`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `titolo`
- `descrizione`
- `durata_ore`

---

### 1.9 `attestato`
- `id` (PK)
- `azienda_id` (FK → `azienda.id`)
- `corso_id` (FK → `corso.id`)
- `operatore_id` (FK → `operatore.id`)
- `data_rilascio`
- `data_scadenza`
- `file_path` (PDF attestato, opzionale)

---

## 2. Relazioni chiave

### 2.1 Relazioni con `azienda` (tenant)

- **`azienda`**
  - 1 → N `utente`
  - 1 → N `operatore`
  - 1 → N `dpi`
  - 1 → N `impianto_anticaduta`
  - 1 → N `ispezione`
  - 1 → N `corso`
  - 1 → N `attestato`
  - 1 → N `allegato`

Regola: **tutte le tabelle “importanti” devono avere `azienda_id`**.

---

### 2.2 Relazioni DPI / Impianti / Ispezioni

- **DPI / Impianti**
  - `dpi` 1 → N `ispezione`
  - `impianto_anticaduta` 1 → N `ispezione`
  - `ispezione` 1 → N `allegato`

- Coerenza `tipo_target`:
  - se `tipo_target = 'DPI'`:
    - `dpi_id` valorizzato
    - `impianto_id` = NULL
  - se `tipo_target = 'IMPIANTO'`:
    - `impianto_id` valorizzato
    - `dpi_id` = NULL

---

### 2.3 Operatori & formazione

- **Operatori & DPI**
  - `operatore` 1 → N `dpi` (DPI assegnati all’operatore)
- **Operatori & corsi**
  - `operatore` 1 → N `attestato`
  - `corso` 1 → N `attestato`

In questo modo:
- puoi vedere **tutti i DPI** di un operatore,
- e **tutta la formazione** (corsi + attestati) legata a lui.

---

## 3. Diagramma (testuale) semplificato

```text
AZIENDA (tenant)
  ├─ UTENTE (ruoli, auth)
  ├─ OPERATORE
  │    ├─ DPI (assegnati)
  │    └─ ATTESTATO ──> CORSO
  ├─ DPI
  │    └─ ISPEZIONE ──> ALLEGATO
  └─ IMPIANTO_ANTICADUTA
       └─ ISPEZIONE ──> ALLEGATO
