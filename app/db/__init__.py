# E:\CLONAZIONE\tpi_evoluto\app\db\accessori.py
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


# --------------------------------------------------
# Path DB (robusto per la tua macchina)
# --------------------------------------------------
# Radice progetto = cartella che contiene app/, tpi.db, ecc.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Permette override via ENV, ma di default usa E:\CLONAZIONE\tpi_evoluto\tpi.db
DB_PATH = Path(
    os.getenv("TPI_DB_PATH", str(PROJECT_ROOT / "tpi.db")),
)


def _connect() -> sqlite3.Connection:
    """
    Connessione a SQLite con row_factory=sqlite3.Row.
    """
    if not DB_PATH.exists():
        raise RuntimeError(f"DB TPI non trovato in {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# Helpers interni
# --------------------------------------------------
def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table,),
    )
    return cur.fetchone() is not None


def _detect_code_column(
    conn: sqlite3.Connection,
    table: str,
) -> Optional[str]:
    """
    Tenta di individuare la colonna 'codice' o simile nella tabella.

    Strategia:
    - PRAGMA table_info(table)
    - cerca nomi che contengono 'codice' (case-insensitive)
    - se niente trovato → None
    """
    cur = conn.execute(f"PRAGMA table_info({table})")
    candidates: List[str] = []
    for row in cur.fetchall():
        name = str(row["name"])
        if "codice" in name.lower():
            candidates.append(name)

    if not candidates:
        return None

    # prendi la prima trovata (di solito 'codice' se c'è)
    return candidates[0]


def _rows_to_dicts(rows: Iterable[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(r) for r in rows]


# --------------------------------------------------
# API principale per ACCESSORI
# --------------------------------------------------
def get_accessori_overview() -> Dict[str, Any]:
    """
    Ritorna i conteggi di base dalle 4 tabelle accessori.

    gestisce in modo tollerante assenza di tabelle.
    """
    tables = [
        ("tpi_accessori_famiglie", "famiglie"),
        ("tpi_accessori_morsetti", "morsetti"),
        ("tpi_accessori_catena_g8", "catena_g8"),
        ("tpi_accessori_tycan", "tycan"),
    ]

    out: Dict[str, Any] = {"db_path": str(DB_PATH), "counts": {}}

    with _connect() as conn:
        for table, key in tables:
            if not _table_exists(conn, table):
                out["counts"][key] = None
                continue

            cur = conn.execute(f"SELECT COUNT(*) AS c FROM {table}")
            row = cur.fetchone()
            out["counts"][key] = int(row["c"]) if row is not None else 0

    total = sum(v for v in out["counts"].values() if isinstance(v, int))
    out["counts"]["total_codici"] = total
    return out


def get_famiglie() -> List[Dict[str, Any]]:
    """
    Ritorna tutte le famiglie accessori (tabella tpi_accessori_famiglie).
    """
    with _connect() as conn:
        if not _table_exists(conn, "tpi_accessori_famiglie"):
            return []

        cur = conn.execute("SELECT * FROM tpi_accessori_famiglie ORDER BY 1")
        return _rows_to_dicts(cur.fetchall())


def get_listino_all() -> List[Dict[str, Any]]:
    """
    Listino completo: unisce tutte le righe dalle tabelle codici.

    Ogni record ha campi originali +:
      - source_table  (nome tabella)
      - source_kind   ('morsetti' / 'catena_g8' / 'tycan')
    """
    tables: List[Tuple[str, str]] = [
        ("tpi_accessori_morsetti", "morsetti"),
        ("tpi_accessori_catena_g8", "catena_g8"),
        ("tpi_accessori_tycan", "tycan"),
    ]

    all_rows: List[Dict[str, Any]] = []

    with _connect() as conn:
        for table, kind in tables:
            if not _table_exists(conn, table):
                continue

            cur = conn.execute(f"SELECT * FROM {table}")
            for r in cur.fetchall():
                row = dict(r)
                row["source_table"] = table
                row["source_kind"] = kind
                all_rows.append(row)

    return all_rows


def find_by_code(codice: str) -> Dict[str, Any]:
    """
    Cerca il codice in tutte le tabelle codici.

    Match case-insensitive, prova sulle colonne che contengono 'codice' nel nome.
    Ritorna il primo match trovato + metadata.
    """
    code_norm = codice.strip()
    if not code_norm:
        raise ValueError("Codice vuoto")

    tables: List[Tuple[str, str]] = [
        ("tpi_accessori_morsetti", "morsetti"),
        ("tpi_accessori_catena_g8", "catena_g8"),
        ("tpi_accessori_tycan", "tycan"),
    ]

    with _connect() as conn:
        for table, kind in tables:
            if not _table_exists(conn, table):
                continue

            code_col = _detect_code_column(conn, table)
            if not code_col:
                # Nessuna colonna 'codice' trovata → salta
                continue

            sql = f"""
                SELECT *
                FROM {table}
                WHERE LOWER({code_col}) = LOWER(?)
            """
            cur = conn.execute(sql, (code_norm,))
            row = cur.fetchone()
            if row is not None:
                data = dict(row)
                data["source_table"] = table
                data["source_kind"] = kind
                data["code_column"] = code_col
                return data

    # Nessun match
    return {}
