from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException

# --------------------------------------------------
# Config DB (WIN / tua macchina)
# --------------------------------------------------
# DB reale TPI_evoluto
DB_PATH = Path(r"E:\CLONAZIONE\tpi_evoluto\tpi.db")


def _get_conn() -> sqlite3.Connection:
    """
    Ritorna una connessione SQLite con row_factory a dict-like.

    NB: conn in-memory, no pooling (perfetto per on-prem + FastAPI leggera).
    """
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"DB TPI non trovato ({DB_PATH})",
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# Helpers interni
# --------------------------------------------------
def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(r) for r in rows]


def _count_table(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.execute(f"SELECT COUNT(*) AS c FROM {table}")
    row = cur.fetchone()
    return int(row["c"]) if row else 0


# --------------------------------------------------
# API – Overview
# --------------------------------------------------
def get_accessori_overview() -> Dict[str, int]:
    """
    Ritorna i conteggi base per le tabelle accessori.

    Usato da /api/accessori/overview.
    """
    with _get_conn() as conn:
        return {
            "famiglie": _count_table(conn, "tpi_accessori_famiglie"),
            "morsetti": _count_table(conn, "tpi_accessori_morsetti"),
            "catena_g8": _count_table(conn, "tpi_accessori_catena_g8"),
            "tycan": _count_table(conn, "tpi_accessori_tycan"),
        }


# --------------------------------------------------
# API – Famiglie
# --------------------------------------------------
def get_famiglie_accessori() -> List[Dict[str, Any]]:
    """
    Ritorna tutte le famiglie accessori (tpi_accessori_famiglie).
    """
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tpi_accessori_famiglie ORDER BY id_tpi ASC")
        rows = cur.fetchall()
    return _rows_to_dicts(rows)


# --------------------------------------------------
# API – Codici per tipologia
# --------------------------------------------------
def get_morsetti_codici() -> List[Dict[str, Any]]:
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tpi_accessori_morsetti ORDER BY codice ASC")
        rows = cur.fetchall()
    return _rows_to_dicts(rows)


def get_catena_g8_codici() -> List[Dict[str, Any]]:
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tpi_accessori_catena_g8 ORDER BY codice ASC")
        rows = cur.fetchall()
    return _rows_to_dicts(rows)


def get_tycan_codici() -> List[Dict[str, Any]]:
    with _get_conn() as conn:
        cur = conn.execute("SELECT * FROM tpi_accessori_tycan ORDER BY codice ASC")
        rows = cur.fetchall()
    return _rows_to_dicts(rows)


# --------------------------------------------------
# API – Listino 3.0 (full)
# --------------------------------------------------
def get_listino_full() -> List[Dict[str, Any]]:
    """
    Listino 3.0 ACCESSORI "full":

    Unisce tutti i codici in un'unica lista,
    aggiungendo il campo 'sorgente' per distinguere la tabella.
    """
    items: List[Dict[str, Any]] = []

    with _get_conn() as conn:
        # morsetti
        cur = conn.execute("SELECT * FROM tpi_accessori_morsetti")
        for row in cur.fetchall():
            d = dict(row)
            d["sorgente"] = "morsetti"
            items.append(d)

        # catena G8
        cur = conn.execute("SELECT * FROM tpi_accessori_catena_g8")
        for row in cur.fetchall():
            d = dict(row)
            d["sorgente"] = "catena_g8"
            items.append(d)

        # TYCAN
        cur = conn.execute("SELECT * FROM tpi_accessori_tycan")
        for row in cur.fetchall():
            d = dict(row)
            d["sorgente"] = "tycan"
            items.append(d)

    return items


# --------------------------------------------------
# API – Lookup per codice (codice articolo)
# --------------------------------------------------
def find_accessorio_by_codice(codice: str) -> Dict[str, Any]:
    """
    Cerca un codice accessorio in tutte le tabelle codici.

    Ritorna il primo match (case-insensitive) con la sorgente.
    """
    codice_norm = codice.strip().lower()
    if not codice_norm:
        raise HTTPException(status_code=400, detail="Codice vuoto o non valido")

    queries: List[Tuple[str, str]] = [
        ("tpi_accessori_morsetti", "morsetti"),
        ("tpi_accessori_catena_g8", "catena_g8"),
        ("tpi_accessori_tycan", "tycan"),
    ]

    with _get_conn() as conn:
        for table, label in queries:
            cur = conn.execute(
                f"""
                SELECT * FROM {table}
                WHERE LOWER(codice) = ?
                """,
                (codice_norm,),
            )
            row = cur.fetchone()
            if row is not None:
                d = dict(row)
                d["sorgente"] = label
                return d

    raise HTTPException(
        status_code=404,
        detail=f"Nessun accessorio trovato per codice '{codice}'",
    )
