#!/usr/bin/env python
# tpi_importer.py – Fase 2: import reale in SQLite + log
#
# Uso tipico da PowerShell:
#   cd E:\CLONAZIONE\tpi_evoluto
#   $files = Get-ChildItem "E:\CLONAZIONE\import\TPI_READY\*.csv"
#   foreach ($f in $files) {
#       python tpi_importer.py --file $f.FullName --table auto
#   }
#
# Cosa fa:
#   - legge il CSV
#   - decide la tabella logica (se --table=auto)
#   - crea/aggiorna il DB SQLite tpi.db nella cartella dello script
#   - crea la tabella se non esiste (tutte le colonne TEXT)
#   - inserisce tutte le righe del CSV
#   - scrive un log in logs/import_log.txt
#
# NOTA: tutti i campi del CSV vengono salvati come TEXT. La normalizzazione
#       numerica (float, int, ecc.) può essere aggiunta in una fase successiva
#       con script dedicati o viste SQL.

import argparse
import csv
from pathlib import Path
from datetime import datetime
import sqlite3
import sys
import re


def infer_table_name(csv_path: Path, table_arg: str | None) -> str:
    """
    Se --table è 'auto', decide la tabella logica in base al nome file.
    Altrimenti usa il valore passato da linea di comando.
    """
    if table_arg and table_arg.lower() != "auto":
        return table_arg

    name = csv_path.name.lower()

    # ACCESSORI – famiglie
    if "famiglie" in name and "accessori" in name:
        return "tpi_accessori_famiglie"

    # MORSETTI – codici
    if "morsetti" in name and "codici" in name:
        return "tpi_accessori_morsetti"

    # CATENA G8 – codici
    if "catena_g8" in name and "codici" in name:
        return "tpi_accessori_catena_g8"

    # TYCAN – catene sintetiche (codici)
    if "tycan" in name and "codici" in name:
        return "tpi_accessori_tycan"

    # Fallback generico
    if "accessori" in name:
        return "tpi_accessori_generico"

    return "tpi_import_generico"


def sanitize_column_name(col: str) -> str:
    """
    Normalizza il nome colonna per SQLite:
    - minuscolo
    - sostituisce caratteri non alfanumerici con underscore
    - evita nomi vuoti
    """
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9]+", "_", col)
    col = col.strip("_")
    if not col:
        col = "colonna"
    return col


def ensure_table(conn: sqlite3.Connection, table: str, header: list[str]) -> list[str]:
    """
    Crea la tabella se non esiste.
    Tutte le colonne del CSV vengono create come TEXT.
    Aggiunge anche:
      - id INTEGER PRIMARY KEY AUTOINCREMENT
      - file_name TEXT
      - imported_at TEXT
    Ritorna la lista di nomi colonna effettivi (sanificati) in ordine.
    """
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    exists = cur.fetchone() is not None

    sanitized_cols = [sanitize_column_name(c) for c in header]

    if not exists:
        cols_def = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for c in sanitized_cols:
            cols_def.append(f'"{c}" TEXT')
        cols_def.append('"file_name" TEXT')
        cols_def.append('"imported_at" TEXT')

        create_sql = f'CREATE TABLE "{table}" ({", ".join(cols_def)});'
        cur.execute(create_sql)
        conn.commit()
    else:
        # In questa fase assumiamo che la struttura sia compatibile.
        # Eventuali aggiunte di colonne si possono gestire in uno step successivo.
        pass

    return sanitized_cols


def import_csv_into_db(db_path: Path, csv_path: Path, table_name: str) -> int:
    """
    Importa un CSV nella tabella indicata dentro tpi.db.
    Ritorna il numero di righe inserite.
    """
    if not csv_path.exists():
        print(f"[ERRORE] File CSV non trovato: {csv_path}", file=sys.stderr)
        return 0

    conn = sqlite3.connect(db_path)
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                header = []

            if not header:
                return 0

            cols = ensure_table(conn, table_name, header)
            cur = conn.cursor()

            inserted = 0
            imported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_name = csv_path.name

            placeholders = ", ".join(["?"] * (len(cols) + 2))
            col_list = ", ".join([f'"{c}"' for c in cols] + ["file_name", "imported_at"])
            insert_sql = f'INSERT INTO "{table_name}" ({col_list}) VALUES ({placeholders})'

            for row in reader:
                # mappa row -> cols (se mancano valori, completa con stringa vuota)
                values_map = {}
                for idx, col in enumerate(cols):
                    values_map[col] = row[idx] if idx < len(row) else ""
                values = [values_map[c] for c in cols] + [file_name, imported_at]
                cur.execute(insert_sql, values)
                inserted += 1

            conn.commit()

    finally:
        conn.close()

    return inserted


def append_log(log_path: Path, csv_path: Path, table_name: str, row_count: int) -> None:
    """
    Scrive una riga di log con data/ora, file, tabella e righe importate.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"{now} | file={csv_path.name} | table={table_name} | rows={row_count}\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="TPI – Importer CSV (fase 2: SQLite + log)")
    parser.add_argument(
        "--file", "-f", required=True, help="Percorso completo al file CSV da importare"
    )
    parser.add_argument(
        "--table",
        "-t",
        default="auto",
        help="Nome tabella logica (oppure 'auto' per dedurre dal nome del file)",
    )
    args = parser.parse_args()

    csv_path = Path(args.file).resolve()
    table_name = infer_table_name(csv_path, args.table)

    # DB SQLite: tpi.db nella stessa cartella dello script
    script_dir = Path(__file__).resolve().parent
    db_path = script_dir / "tpi.db"

    # Log: logs/import_log.txt nella stessa cartella dello script
    log_path = script_dir / "logs" / "import_log.txt"

    row_count = import_csv_into_db(db_path, csv_path, table_name)
    append_log(log_path, csv_path, table_name, row_count)

    print(f"[OK][DB] {csv_path.name} → tabella {table_name}, righe inserite: {row_count}")
    print(f"[DB] Percorso DB: {db_path}")
    print(f"[LOG] Aggiornato: {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
