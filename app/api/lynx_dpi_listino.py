from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

# Percorso DB – stesso di ACCESSORI
DB_PATH = Path(r"E:\CLONAZIONE\tpi_evoluto\tpi.db")


# ------------------------------------------------------------
# Helpers DB
# ------------------------------------------------------------
def _get_connection() -> sqlite3.Connection:
    """Connessione SQLite con row_factory a dict + check esistenza DB."""
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Database non trovato: {DB_PATH}",
        )

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(r) for r in rows]


# ------------------------------------------------------------
# Letture base per view LYNX DPI
# ------------------------------------------------------------
def _get_all_listino_rows() -> List[Dict[str, Any]]:
    """
    Ritorna tutte le righe della view vw_lynx_dpi_listino.

    View creata da:
      sql/create_views_lynx_dpi_3_0_2025-12-09.sql
    """
    con = _get_connection()
    try:
        cur = con.execute("SELECT * FROM vw_lynx_dpi_listino")
        rows = cur.fetchall()
        return _rows_to_dicts(rows)
    except sqlite3.OperationalError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "View vw_lynx_dpi_listino mancante. "
                "Assicurati di aver eseguito sql/create_views_lynx_dpi_3_0_2025-12-09.sql."
            ),
        ) from exc
    except sqlite3.DatabaseError as exc:
        raise HTTPException(status_code=500, detail=f"Errore DB LYNX DPI: {exc}") from exc
    finally:
        con.close()


def get_listino_overview() -> Dict[str, int]:
    """
    Panoramica rapida per /api/dpi/lynx/overview.
    """
    rows = _get_all_listino_rows()
    tot = len(rows)

    # Contiamo famiglie distinte lato Python: robusto a nomi diversi
    famiglie = {str(r.get("famiglia", "")).strip() for r in rows if r.get("famiglia")}
    return {
        "famiglie_distinte": len(famiglie),
        "totale_dpi": tot,
    }


# ------------------------------------------------------------
# Filtri / paginazione (stesso modello ACCESSORI)
# ------------------------------------------------------------
def filter_listino(
    famiglia: Optional[str] = None,
    sorgente: Optional[str] = None,
    cerca: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Filtra la view vw_lynx_dpi_listino con logica soft:

    - famiglia → LIKE case-insensitive su colonna 'famiglia'
    - sorgente → match esatto (es. 'LYNX_DPI', 'FORESTALE_DPI' se in futuro)
    - cerca → full-text semplice su tutte le colonne stringa
    """
    rows = _get_all_listino_rows()

    fam_norm = famiglia.lower() if famiglia else None
    src_norm = sorgente.lower() if sorgente else None
    cerca_norm = cerca.lower() if cerca else None

    def _match(row: Dict[str, Any]) -> bool:
        if fam_norm:
            fam_val = str(row.get("famiglia", "")).lower()
            if fam_norm not in fam_val:
                return False
        if src_norm:
            src_val = str(row.get("sorgente", "")).lower()
            if src_norm != src_val:
                return False
        if cerca_norm:
            joined = " ".join(str(v) for v in row.values())
            if cerca_norm not in joined.lower():
                return False
        return True

    filtered = [r for r in rows if _match(r)]
    total = len(filtered)

    start = max(offset, 0)
    end = start + max(limit, 0)
    return total, filtered[start:end]


def search_by_code(codice: str) -> Optional[Dict[str, Any]]:
    """
    Cerca un DPI per codice:

    - match case-insensitive su uno dei campi plausibili:
      id_tpi, codice_tpi, codice_fabbrica, codice
    """
    target = codice.lower()
    rows = _get_all_listino_rows()

    for row in rows:
        for key in ["id_tpi", "codice_tpi", "codice_fabbrica", "codice"]:
            val = row.get(key)
            if isinstance(val, str) and val.lower() == target:
                return dict(row)

    return None
