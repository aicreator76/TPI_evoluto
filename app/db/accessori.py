# E:\CLONAZIONE\tpi_evoluto\app\db\accessori.py
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("TPI_DB_PATH", str(PROJECT_ROOT / "tpi.db")))

ACCESSORI_TABLES: Tuple[Tuple[str, str], ...] = (
    ("tpi_accessori_famiglie", "famiglie"),
    ("tpi_accessori_morsetti", "morsetti"),
    ("tpi_accessori_catena_g8", "catena_g8"),
    ("tpi_accessori_tycan", "tycan"),
)

ACCESSORI_LISTINO_TABLES: Tuple[Tuple[str, str], ...] = (
    ("tpi_accessori_morsetti", "morsetti"),
    ("tpi_accessori_catena_g8", "catena_g8"),
    ("tpi_accessori_tycan", "tycan"),
)

# Query STATICHE (niente SQL costruito a runtime -> Bandit B608 muto)
_COUNT_SQL: Dict[str, str] = {
    "tpi_accessori_famiglie": "SELECT COUNT(*) AS c FROM tpi_accessori_famiglie",
    "tpi_accessori_morsetti": "SELECT COUNT(*) AS c FROM tpi_accessori_morsetti",
    "tpi_accessori_catena_g8": "SELECT COUNT(*) AS c FROM tpi_accessori_catena_g8",
    "tpi_accessori_tycan": "SELECT COUNT(*) AS c FROM tpi_accessori_tycan",
}

_SELECT_ALL_SQL: Dict[str, str] = {
    "tpi_accessori_famiglie": "SELECT * FROM tpi_accessori_famiglie",
    "tpi_accessori_morsetti": "SELECT * FROM tpi_accessori_morsetti",
    "tpi_accessori_catena_g8": "SELECT * FROM tpi_accessori_catena_g8",
    "tpi_accessori_tycan": "SELECT * FROM tpi_accessori_tycan",
}

_FIND_BY_CODE_SQL: Dict[str, str] = {
    "tpi_accessori_morsetti": "SELECT * FROM tpi_accessori_morsetti WHERE LOWER(codice) = LOWER(?)",
    "tpi_accessori_catena_g8": "SELECT * FROM tpi_accessori_catena_g8 WHERE LOWER(codice) = LOWER(?)",
    "tpi_accessori_tycan": "SELECT * FROM tpi_accessori_tycan WHERE LOWER(codice) = LOWER(?)",
}


def _connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise RuntimeError(f"DB TPI non trovato in {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table,),
    )
    return cur.fetchone() is not None


def _rows_to_dicts(rows: Iterable[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(r) for r in rows]


def _detect_code_column_from_row(row_dict: Dict[str, Any]) -> Optional[str]:
    # fallback: cerca colonna che contiene "codice"
    for k in row_dict.keys():
        if "codice" in str(k).lower():
            return str(k)
    return None


def get_accessori_overview() -> Dict[str, Any]:
    """
    Output compatibile col test:
    {'famiglie':30,'morsetti':..,'catena_g8':..,'tycan':..,'total_codici':..}
    """
    out: Dict[str, Any] = {}

    with _connect() as conn:
        for table, key in ACCESSORI_TABLES:
            if not _table_exists(conn, table):
                out[key] = None
                continue

            sql = _COUNT_SQL.get(table)
            if not sql:
                out[key] = None
                continue

            row = conn.execute(sql).fetchone()
            out[key] = int(row["c"]) if row is not None else 0

    out["total_codici"] = sum(v for v in out.values() if isinstance(v, int))
    return out


def get_famiglie() -> List[Dict[str, Any]]:
    with _connect() as conn:
        if not _table_exists(conn, "tpi_accessori_famiglie"):
            return []
        cur = conn.execute(_SELECT_ALL_SQL["tpi_accessori_famiglie"] + " ORDER BY 1")
        return _rows_to_dicts(cur.fetchall())


def get_listino_all() -> List[Dict[str, Any]]:
    all_rows: List[Dict[str, Any]] = []

    with _connect() as conn:
        for table, kind in ACCESSORI_LISTINO_TABLES:
            if not _table_exists(conn, table):
                continue

            sql = _SELECT_ALL_SQL.get(table)
            if not sql:
                continue

            cur = conn.execute(sql)
            for r in cur.fetchall():
                row = dict(r)
                row["source_table"] = table
                row["source_kind"] = kind
                all_rows.append(row)

    return all_rows


def find_by_code(codice: str) -> Dict[str, Any]:
    code_norm = (codice or "").strip()
    if not code_norm:
        raise ValueError("Codice vuoto")

    with _connect() as conn:
        for table, kind in ACCESSORI_LISTINO_TABLES:
            if not _table_exists(conn, table):
                continue

            # 1) tentativo “standard” su colonna codice
            sql = _FIND_BY_CODE_SQL.get(table)
            if sql:
                try:
                    row = conn.execute(sql, (code_norm,)).fetchone()
                    if row is not None:
                        data = dict(row)
                        data["source_table"] = table
                        data["source_kind"] = kind
                        data["code_column"] = "codice"
                        return data
                except sqlite3.OperationalError:
                    pass

            # 2) fallback: leggi righe e cerca colonna tipo "codice*"
            sql_all = _SELECT_ALL_SQL.get(table)
            if not sql_all:
                continue

            cur = conn.execute(sql_all)
            rows = cur.fetchall()
            if not rows:
                continue

            first = dict(rows[0])
            code_col = _detect_code_column_from_row(first)
            if not code_col:
                continue

            for r in rows:
                d = dict(r)
                v = str(d.get(code_col, "")).strip()
                if v.lower() == code_norm.lower():
                    d["source_table"] = table
                    d["source_kind"] = kind
                    d["code_column"] = code_col
                    return d

    return {}


# ---------------------------------------------------------------------------
# Compatibility layer for API expectations (mypy attr-defined fix)
# ---------------------------------------------------------------------------


def get_famiglie_accessori() -> List[Dict[str, Any]]:
    """Alias compatibilità: l'API si aspetta questo nome."""
    return get_famiglie()


def get_listino_full() -> List[Dict[str, Any]]:
    """Alias compatibilità: l'API si aspetta questo nome."""
    return get_listino_all()


def find_accessorio_by_codice(codice: str) -> Dict[str, Any]:
    """Alias compatibilità: l'API si aspetta questo nome."""
    return find_by_code(codice)


def get_catena_g8_codici() -> List[str]:
    """Restituisce la lista dei codici presenti in catena_g8."""
    rows = get_listino_all()
    out: List[str] = []
    for r in rows:
        if r.get("source_kind") != "catena_g8":
            continue
        code_col = str(r.get("code_column") or "codice")
        v = r.get(code_col)
        if v is not None:
            s = str(v).strip()
            if s:
                out.append(s)
    # dedup preservando ordine
    seen: set[str] = set()
    uniq: List[str] = []
    for x in out:
        lx = x.lower()
        if lx in seen:
            continue
        seen.add(lx)
        uniq.append(x)
    return uniq


def get_morsetti_codici() -> List[str]:
    """Restituisce la lista dei codici presenti in morsetti."""
    rows = get_listino_all()
    out: List[str] = []
    for r in rows:
        if r.get("source_kind") != "morsetti":
            continue
        code_col = str(r.get("code_column") or "codice")
        v = r.get(code_col)
        if v is not None:
            s = str(v).strip()
            if s:
                out.append(s)
    seen: set[str] = set()
    uniq: List[str] = []
    for x in out:
        lx = x.lower()
        if lx in seen:
            continue
        seen.add(lx)
        uniq.append(x)
    return uniq


def get_tycan_codici() -> List[str]:
    """Restituisce la lista dei codici presenti in tycan."""
    rows = get_listino_all()
    out: List[str] = []
    for r in rows:
        if r.get("source_kind") != "tycan":
            continue
        code_col = str(r.get("code_column") or "codice")
        v = r.get(code_col)
        if v is not None:
            s = str(v).strip()
            if s:
                out.append(s)
    seen: set[str] = set()
    uniq: List[str] = []
    for x in out:
        lx = x.lower()
        if lx in seen:
            continue
        seen.add(lx)
        uniq.append(x)
    return uniq
