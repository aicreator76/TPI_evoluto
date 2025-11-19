\# Schema TPI\_evoluto – Versione 1 (Postgres)

Data: 2025-11-19

Milestone: M1 – Foundation (#48)



Obiettivo: definire lo schema dati minimo per gestire:

\- aziende (tenant)

\- utenti e ruoli

\- DPI

\- impianti anticaduta

\- operatori

\- ispezioni

\- allegati

\- corsi e attestati (struttura base)



> Nota: tipi indicati per Postgres. `uuid` consigliato per tutte le PK.



---



\## 1. Tenant \& Utenti



\### 1.1 Tabella `tenant`



| Campo         | Tipo        | Note                               |

|---------------|------------|------------------------------------|

| id            | uuid PK    | PK                                 |

| name          | text       | Ragione sociale                    |

| slug          | text       | Nome breve/URL safe, unico        |

| vat\_number    | text       | P.IVA / identificativo fiscale    |

| country       | text       | Paese                              |

| created\_at    | timestamptz| default now()                      |

| is\_active     | bool       | default true                       |



\*\*Vincoli\*\*

\- `UNIQUE(slug)`

\- In futuro collegata a `tenant\_config` (M3).



---



\### 1.2 Tabella `user\_account`



| Campo         | Tipo        | Note                                                  |

|---------------|------------|-------------------------------------------------------|

| id            | uuid PK    | PK                                                    |

| tenant\_id     | uuid FK    | FK → tenant(id)                                       |

| email         | text       | Unica per tenant                                      |

| password\_hash | text       | Hash (es. Argon2/bcrypt)                              |

| full\_name     | text       | Nome completo                                         |

| role          | text       | enum logico: RSPP, HSE, DATORE, OPERATORE, REVISORE  |

| is\_active     | bool       | default true                                          |

| created\_at    | timestamptz| default now()                                         |

| last\_login\_at | timestamptz| nullable                                              |



\*\*Vincoli\*\*

\- `UNIQUE(tenant\_id, email)`

\- `FOREIGN KEY (tenant\_id) REFERENCES tenant(id) ON DELETE CASCADE`



---



\## 2. Operatori \& Corsi



\### 2.1 Tabella `operator`



Rappresenta i lavoratori a cui vengono assegnati DPI / corsi.



| Campo         | Tipo        | Note                           |

|---------------|------------|--------------------------------|

| id            | uuid PK    |                                |

| tenant\_id     | uuid FK    | FK → tenant(id)               |

| first\_name    | text       |                                |

| last\_name     | text       |                                |

| email         | text       | opzionale                      |

| job\_title     | text       | mansione                       |

| badge\_code    | text       | codice interno / badge        |

| is\_active     | bool       | default true                  |

| created\_at    | timestamptz|                                |



\*\*Vincoli\*\*

\- `UNIQUE(tenant\_id, badge\_code)` (se usato)

\- `FOREIGN KEY (tenant\_id) REFERENCES tenant(id)`



---



\### 2.2 Tabella `course`



| Campo           | Tipo        | Note                                   |

|-----------------|------------|----------------------------------------|

| id              | uuid PK    |                                        |

| tenant\_id       | uuid FK    | FK → tenant(id)                        |

| title           | text       | Nome corso                             |

| course\_type     | text       | es. DPI, anticaduta, carrelli, ecc.   |

| provider        | text       | Ente erogatore                         |

| hours           | numeric    | Ore corso                              |

| validity\_years  | int        | Anni di validità suggeriti             |

| created\_at      | timestamptz|                                        |



---



\### 2.3 Tabella `certificate`



Attestati dei corsi.



| Campo           | Tipo        | Note                             |

|-----------------|------------|----------------------------------|

| id              | uuid PK    |                                  |

| tenant\_id       | uuid FK    | FK → tenant(id)                 |

| operator\_id     | uuid FK    | FK → operator(id)               |

| course\_id       | uuid FK    | FK → course(id)                 |

| issue\_date      | date       | Data emissione                  |

| expiry\_date     | date       | Data scadenza                   |

| file\_path       | text       | Riferimento a PDF nel storage   |

| notes           | text       | opzionale                        |

| created\_at      | timestamptz|                                  |



\*\*Vincoli\*\*

\- `FOREIGN KEY (tenant\_id) REFERENCES tenant(id)`

\- `FOREIGN KEY (operator\_id) REFERENCES operator(id)`

\- `FOREIGN KEY (course\_id) REFERENCES course(id)`



---



\## 3. DPI \& Assegnazioni



\### 3.1 Tabella `dpi`



| Campo                | Tipo        | Note                                            |

|----------------------|------------|-------------------------------------------------|

| id                   | uuid PK    |                                                 |

| tenant\_id            | uuid FK    | FK → tenant(id)                                 |

| code                 | text       | Codice interno / matricola                      |

| serial\_number        | text       | Numero di serie                                 |

| description          | text       | Descrizione breve                               |

| model                | text       | Modello                                         |

| manufacturer         | text       | Produttore                                      |

| category             | text       | es. imbracatura, cordino, casco, ecc.          |

| status               | text       | enum: ATTIVO, MAGAZZINO, RIPARAZIONE, SCARTATO |

| purchase\_date        | date       | opzionale                                       |

| expiry\_date          | date       | Scadenza certificazione                         |

| next\_inspection\_date | date       | Prossima ispezione programmata                  |

| created\_at           | timestamptz|                                                 |



\*\*Vincoli\*\*

\- `UNIQUE(tenant\_id, code)`

\- `FOREIGN KEY (tenant\_id) REFERENCES tenant(id)`



---



\### 3.2 Tabella `dpi\_assignment`



Storico assegnazioni DPI ↔ operatore.



| Campo         | Tipo        | Note                            |

|---------------|------------|---------------------------------|

| id            | uuid PK    |                                 |

| tenant\_id     | uuid FK    | FK → tenant(id)                |

| dpi\_id        | uuid FK    | FK → dpi(id)                   |

| operator\_id   | uuid FK    | FK → operator(id)              |

| assigned\_at   | timestamptz| Data/ora consegna              |

| returned\_at   | timestamptz| Data/ora restituzione, nullable|

| status        | text       | ATTIVO, RESO, SMARRITO, ecc.   |



---



\## 4. Impianti anticaduta



\### 4.1 Tabella `fall\_protection\_system`



| Campo           | Tipo        | Note                                            |

|-----------------|------------|-------------------------------------------------|

| id              | uuid PK    |                                                 |

| tenant\_id       | uuid FK    | FK → tenant(id)                                 |

| name            | text       | Nome impianto / codice interno                  |

| system\_type     | text       | LINEA\_VITA, PUNTO\_ANcoraggio, SCALA\_FISSA, ecc.|

| location\_text   | text       | Indirizzo/descrizione luogo                     |

| latitude        | numeric    | opzionale                                       |

| longitude       | numeric    | opzionale                                       |

| status          | text       | ATTIVO, OUT\_OF\_SERVICE                          |

| installation\_date | date     | opzionale                                       |

| next\_inspection\_date | date  | Prossima ispezione                              |

| created\_at      | timestamptz|                                                 |



---



\## 5. Ispezioni \& Allegati



\### 5.1 Tabella `inspection`



Ispezione di un DPI \*\*o\*\* di un impianto.



| Campo          | Tipo        | Note                                                  |

|----------------|------------|-------------------------------------------------------|

| id             | uuid PK    |                                                       |

| tenant\_id      | uuid FK    | FK → tenant(id)                                      |

| target\_type    | text       | enum: DPI, IMPIANTO                                  |

| dpi\_id         | uuid FK    | FK → dpi(id), nullable (solo se target\_type = DPI)   |

| system\_id      | uuid FK    | FK → fall\_protection\_system(id), nullable            |

| performed\_at   | timestamptz| Data/ora ispezione                                    |

| result         | text       | OK, KO, DA\_VERIFICARE                                |

| notes          | text       | opzionale                                            |

| inspector\_id   | uuid FK    | FK → user\_account(id)                                |

| created\_at     | timestamptz|                                                       |



\*\*Regole logiche\*\*

\- se `target\_type = 'DPI'` → `dpi\_id` NOT NULL, `system\_id` NULL

\- se `target\_type = 'IMPIANTO'` → `system\_id` NOT NULL, `dpi\_id` NULL



---



\### 5.2 Tabella `attachment`



| Campo          | Tipo        | Note                                              |

|----------------|------------|---------------------------------------------------|

| id             | uuid PK    |                                                   |

| tenant\_id      | uuid FK    | FK → tenant(id)                                  |

| inspection\_id  | uuid FK    | FK → inspection(id), nullable                    |

| dpi\_id         | uuid FK    | FK → dpi(id), nullable                           |

| system\_id      | uuid FK    | FK → fall\_protection\_system(id), nullable        |

| file\_type      | text       | PHOTO, PDF, VIDEO, ALTRO                         |

| file\_name      | text       | Nome originale                                   |

| storage\_path   | text       | Path/URL su storage (es. S3, filesystem, ecc.)   |

| mime\_type      | text       |                                                   |

| uploaded\_by\_id | uuid FK    | FK → user\_account(id)                            |

| uploaded\_at    | timestamptz|                                                   |



---



\## 6. Relazioni chiave (riassunto)



\- `tenant 1─N user\_account`

\- `tenant 1─N operator`

\- `tenant 1─N course 1─N certificate`

\- `tenant 1─N dpi 1─N dpi\_assignment`

\- `tenant 1─N fall\_protection\_system`

\- `dpi / fall\_protection\_system 1─N inspection 1─N attachment`

\- `user\_account 1─N inspection`

\- `user\_account 1─N attachment`



---



\## 7. Note per le prossime milestone



\- \*\*M2\*\* userà direttamente:

&nbsp; - `dpi`, `fall\_protection\_system`, `inspection`, `attachment`, `dpi\_assignment`.

\- \*\*M3\*\* aggiungerà:

&nbsp; - `audit\_log`

&nbsp; - `tenant\_config`

&nbsp; - `integration\_endpoint`



Per ora NON sono incluse in questo schema per tenere M1 focalizzata sulle entità core.
