
TPI – ACCESSORI 3.0 – DB REALE (FASE 2)
=======================================

Scopo
-----
Questo pacchetto permette a QUALSIASI AI / script esterno di:
- sapere DOVE sono i file CSV degli accessori
- sapere DOVE sta il DB
- avere un METODO UNICO per importare TUTTI gli accessori nel DB SQLite `tpi.db`.

Percorsi ufficiali (Sistema del Sovrano)
----------------------------------------

Radice progetto TPI (codice):
  E:\CLONAZIONE\tpi_evoluto\

Cartella di staging per i CSV pronti all'import:
  E:\CLONAZIONE\import\TPI_READY\

Cartella ZIP di origine accessori:
  E:\CLONAZIONE\ACCESSORI_ZIP\

File principali usati finora:
  - E:\CLONAZIONE\ACCESSORI_ZIP\TPI_ACCESSORI_FULL_3.0.zip
  - E:\CLONAZIONE\ACCESSORI_ZIP\TPI_ACCESSORI_FULL_3.0\ACCESSORI_3.0_famiglie_full_package.zip
  - E:\CLONAZIONE\ACCESSORI_ZIP\TPI_ACCESSORI_FULL_3.0\ACCESSORI_MORSETTI_3.0_codici_package.zip
  - E:\CLONAZIONE\ACCESSORI_ZIP\TPI_ACCESSORI_FULL_3.0\ACCESSORI_CATENA_G8_3.0_codici_package.zip
  - E:\CLONAZIONE\ACCESSORI_ZIP\TPI_ACCESSORI_FULL_3.0\TPI_TYCAN_3.0_full_package.zip

CSV attualmente importati via tpi_importer.py:
  - accessori_punti_ancoraggio_famiglie_3.0.csv
  - accessori_morsetti_famiglie_3.0.csv
  - accessori_tiranti_brache_famiglie_3.0.csv
  - accessori_catena_G8_famiglie_3.0.csv
  - accessori_catene_TYCAN_famiglie_3.0.csv
  - accessori_famiglie_3.0_ALL.csv
  - accessori_morsetti_codici_3.0.csv
  - accessori_catena_G8_codici_3.0.csv
  - accessori_tycan_codici_3.0.csv

File DB e log
-------------

DB SQLite:
  E:\CLONAZIONE\tpi_evoluto\tpi.db

Log import:
  E:\CLONAZIONE\tpi_evoluto\logs\import_log.txt

Metodo di import MASSIVO (per altra AI)
---------------------------------------

1) Assicurarsi che i CSV da importare siano in:
     E:\CLONAZIONE\import\TPI_READY\

2) Lanciare da PowerShell:

     cd E:\CLONAZIONE\tpi_evoluto
     $files = Get-ChildItem "E:\CLONAZIONE\import\TPI_READY\*.csv"
     foreach ($f in $files) {
         python tpi_importer.py --file $f.FullName --table auto
     }

3) Lo script tpi_importer.py:
   - deduce il nome tabella da --table o dal nome file (famiglie / morsetti / G8 / Tycan)
   - crea/aggiorna il DB tpi.db
   - crea la tabella se non esiste (tutte le colonne del CSV come TEXT)
   - inserisce una riga per ogni record del CSV
   - scrive una riga di log in logs/import_log.txt

Tabelle create automaticamente
------------------------------

A seconda del nome file CSV, vengono creati i seguenti nomi tabella logici:

  - accessori_*_famiglie_3.0.csv      → tpi_accessori_famiglie
  - accessori_morsetti_codici_3.0.csv → tpi_accessori_morsetti
  - accessori_catena_G8_codici_3.0.csv→ tpi_accessori_catena_g8
  - accessori_tycan_codici_3.0.csv    → tpi_accessori_tycan
  - fallback (altri accessori)        → tpi_accessori_generico

Ogni tabella contiene:
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - una colonna TEXT per ciascun campo del CSV (nome sanificato, minuscolo, con underscore)
  - file_name TEXT → nome del CSV di origine
  - imported_at TEXT → timestamp di import

I nomi colonna derivano dall'intestazione del CSV, puliti con questa regola:
  - minuscolo
  - caratteri non alfanumerici → underscore
  - spazi rimossi dai bordi

Uso da parte di un'altra AI
---------------------------

Una seconda AI (es. agente DB, BI, o generatore di report) può:

  1. Leggere direttamente il DB SQLite da:
       E:\CLONAZIONE\tpi_evoluto\tpi.db

  2. Eseguire query come:
       SELECT * FROM tpi_accessori_morsetti;
       SELECT * FROM tpi_accessori_catena_g8;
       SELECT * FROM tpi_accessori_tycan;

  3. Usare logs/import_log.txt per capire quali CSV e quante righe sono state importate.

  4. Aggiungere viste/report, ad esempio:
       - vista per listino commerciale 3.0
       - vista per controllo coerenza WLL / diametri
       - vista per esportazione verso altri sistemi TPI.

Note importanti
---------------

- Questo pacchetto NON inventa colonne né dati: usa esattamente i campi dei CSV.
- Eventuali ottimizzazioni (tipi numerici, vincoli, chiavi esterne) possono essere fatte in uno step successivo.
- Il flusso è pensato per essere riutilizzato anche per altri cataloghi (DPI, funi, ecc.) mantenendo la stessa logica:
    CSV → TPI_READY → tpi_importer.py → tpi.db → viste/report.
