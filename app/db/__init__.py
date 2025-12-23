from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.db.sql_safety import quote_ident  # E:\CLONAZIONE\tpi_evoluto\app\db\sql_safety.py


# --------------------------------------------------
# DB path (robusto)
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("TPI_DB_PATH", str(PROJECT_ROOT / "tpi.db")))


def _connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Connessione SQLite con row_factory=sqlite3.Row."""
    p = db_path or DB_PATH
    if not p.exists():
        raise RuntimeError(f"DB TPI non trovato in {p}")
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """Verifica esistenza tabella (parametrizzato)."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table,),
    )
    return cur.fetchone() is not None


def count_table(conn: sqlite3.Connection, table: str) -> int:
    """
    Count righe tabella.
    NOTE: table è un identificatore -> va validato/quotato.
    """
    t = quote_ident(table)
    cur = conn.execute(f"SELECT COUNT(*) AS c FROM {t}")  # nosec B608
    row = cur.fetchone()
    return int(row["c"]) if row is not None else 0


def fetch_all(conn: sqlite3.Connection, table: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Estrae righe da tabella (limit di default per sicurezza).
    """
    t = quote_ident(table)
    cur = conn.execute(f"SELECT * FROM {t} LIMIT ?", (int(limit),))  # nosec
    return [dict(r) for r in cur.fetchall()]


def find_first_by_code(
    conn: sqlite3.Connection,
    table: str,
    code_column: str,
    code_value: str,
) -> Dict[str, Any]:
    """
    Cerca un record per codice (case-insensitive) su colonna specifica.
    """
    t = quote_ident(table)
    c = quote_ident(code_column)
    sql = f"SELECT * FROM {t} WHERE LOWER({c}) = LOWER(?) LIMIT 1"  # nosec
    cur = conn.execute(sql, ((code_value or "").strip(),))
    row = cur.fetchone()
    return dict(row) if row is not None else {}


__all__ = [
    "DB_PATH",
    "PROJECT_ROOT",
    "quote_ident",
    "table_exists",
    "count_table",
    "fetch_all",
    "find_first_by_code",
]
