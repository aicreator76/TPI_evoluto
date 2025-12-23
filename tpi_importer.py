#!/usr/bin/env python
# E:\CLONAZIONE\tpi_evoluto\tpi_importer.py
#
# Import CSV -> SQLite + log (fase 2)
# - Sicurezza: identificatori validati con quote_ident (E:\CLONAZIONE\tpi_evoluto\app\db\sql_safety.py)
# - Colonne: sanitize + dedupe
# - Log: logs/import_log.txt

from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from app.db.sql_safety import quote_ident  # E:\CLONAZIONE\tpi_evoluto\app\db\sql_safety.py


def infer_table_name(csv_path: Path, table_arg: str | None) -> str:
    if table_arg and table_arg.lower() != "auto":
        return table_arg

    name = csv_path.name.lower()

    if "famiglie" in name and "accessori" in name:
        return "tpi_accessori_famiglie"
    if "morsetti" in name and "codici" in name:
        return "tpi_accessori_morsetti"
    if "catena_g8" in name and "codici" in name:
        return "tpi_accessori_catena_g8"
    if "tycan" in name and "codici" in name:
        return "tpi_accessori_tycan"
    if "accessori" in name:
        return "tpi_accessori_generico"

    return "tpi_import_generico"


_COL_RE = re.compile(r"[^a-z0-9]+")


def sanitize_column_name(col: str) -> str:
    col = (col or "").strip().lower()
    col = _COL_RE.sub("_", col).strip("_")
    return col or "colonna"


def dedupe_columns(cols: List[str]) -> List[str]:
    seen: dict[str, int] = {}
    out: List[str] = []
    for c in cols:
        n = seen.get(c, 0) + 1
        seen[c] = n
        out.append(c if n == 1 else f"{c}_{n}")
    return out


def ensure_table(conn: sqlite3.Connection, table: str, header: List[str]) -> List[str]:
    t = quote_ident(table)

    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    exists = cur.fetchone() is not None

    sanitized = [sanitize_column_name(c) for c in header]
    cols = dedupe_columns(sanitized)

    if not exists:
        cols_def: List[str] = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for c in cols:
            cols_def.append(f"{quote_ident(c)} TEXT")
        cols_def.append(f"{quote_ident('file_name')} TEXT")
        cols_def.append(f"{quote_ident('imported_at')} TEXT")

        create_sql = f"CREATE TABLE {t} ({', '.join(cols_def)});"
        cur.execute(create_sql)
        conn.commit()

    return cols


def import_csv_into_db(db_path: Path, csv_path: Path, table_name: str) -> int:
    if not csv_path.exists():
        print(f"[ERRORE] CSV non trovato: {csv_path}", file=sys.stderr)
        return 0

    conn = sqlite3.connect(db_path)
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return 0

            cols = ensure_table(conn, table_name, header)

            t = quote_ident(table_name)
            col_list = ", ".join(
                [quote_ident(c) for c in cols]
                + [quote_ident("file_name"), quote_ident("imported_at")]
            )
            placeholders = ", ".join(["?"] * (len(cols) + 2))
            insert_sql = f"INSERT INTO {t} ({col_list}) VALUES ({placeholders})"  # nosec
            cur = conn.cursor()
            imported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_name = csv_path.name

            inserted = 0
            for row in reader:
                row = row or []
                base_values = (row + [""] * len(cols))[: len(cols)]
                values = base_values + [file_name, imported_at]
                cur.execute(insert_sql, values)
                inserted += 1

            conn.commit()
            return inserted
    finally:
        conn.close()


def append_log(log_path: Path, csv_path: Path, table_name: str, row_count: int) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now} | file={csv_path.name} | table={table_name} | rows={row_count}\n"
    log_path.write_text(
        log_path.read_text(encoding="utf-8") + line, encoding="utf-8"
    ) if log_path.exists() else log_path.write_text(line, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="TPI – Importer CSV (fase 2: SQLite + log)")
    parser.add_argument("--file", "-f", required=True, help="Percorso completo al file CSV")
    parser.add_argument("--table", "-t", default="auto", help="Nome tabella (o 'auto')")
    args = parser.parse_args()

    csv_path = Path(args.file).resolve()
    table_name = infer_table_name(csv_path, args.table)

    script_dir = Path(__file__).resolve().parent
    db_path = script_dir / "tpi.db"
    log_path = script_dir / "logs" / "import_log.txt"

    row_count = import_csv_into_db(db_path, csv_path, table_name)
    append_log(log_path, csv_path, table_name, row_count)

    print(f"[OK][DB] {csv_path.name} → tabella {table_name}, righe inserite: {row_count}")
    print(f"[DB] {db_path}")
    print(f"[LOG] {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
