"""
Access layer per ACCESSORI 3.0 (Listino).

Obiettivi:
- Lettura tabelle accessori_* e, se presente, della view vw_accessori_listino_completo.
- Nessuna assunzione rigida sui nomi delle colonne → filtri lato Python.
- Funzioni usate dal router FastAPI in app.api.accessori_listino.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException

# Percorso DB assoluto (on-prem TPI)
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv("TPI_DB_PATH", str(PROJECT_ROOT / "data" / "tpi.db")))


# ------------------------------------------------------------
# Helpers DB
# ------------------------------------------------------------
def _get_connection() -> sqlite3.Connection:
    """
    Ritorna una connessione SQLite con row_factory a dizionario.

    Solleva HTTP 500 se il DB non esiste.
    """
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Database non trovato: {DB_PATH}",
        )

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Converte una lista di sqlite3.Row in list[dict]."""
    return [dict(r) for r in rows]


# ------------------------------------------------------------
# Letture base per tabelle "grezze"
# ------------------------------------------------------------
def get_famiglie() -> List[Dict[str, Any]]:
    """Ritorna tutte le famiglie accessori (tabella tpi_accessori_famiglie)."""
    con = _get_connection()
    try:
        cur = con.execute("SELECT * FROM tpi_accessori_famiglie")
        rows = cur.fetchall()
        return _rows_to_dicts(rows)
    except sqlite3.DatabaseError as exc:
        raise HTTPException(status_code=500, detail=f"Errore DB famiglie: {exc}") from exc
    finally:
        con.close()


def get_morsetti() -> List[Dict[str, Any]]:
    """Ritorna tutti i morsetti (tabella codici tpi_accessori_morsetti)."""
    con = _get_connection()
    try:
        cur = con.execute("SELECT * FROM tpi_accessori_morsetti")
        rows = cur.fetchall()
        return _rows_to_dicts(rows)
    except sqlite3.DatabaseError as exc:
        raise HTTPException(status_code=500, detail=f"Errore DB morsetti: {exc}") from exc
    finally:
        con.close()


def get_catena_g8() -> List[Dict[str, Any]]:
    """Ritorna tutte le catene G8 (tabella codici tpi_accessori_catena_g8)."""
    con = _get_connection()
    try:
        cur = con.execute("SELECT * FROM tpi_accessori_catena_g8")
        rows = cur.fetchall()
        return _rows_to_dicts(rows)
    except sqlite3.DatabaseError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Errore DB catena G8: {exc}",
        ) from exc
    finally:
        con.close()


def get_tycan() -> List[Dict[str, Any]]:
    """Ritorna tutte le catene TYCAN (tabella codici tpi_accessori_tycan)."""
    con = _get_connection()
    try:
        cur = con.execute("SELECT * FROM tpi_accessori_tycan")
        rows = cur.fetchall()
        return _rows_to_dicts(rows)
    except sqlite3.DatabaseError as exc:
        raise HTTPException(status_code=500, detail=f"Errore DB Tycan: {exc}") from exc
    finally:
        con.close()


# ------------------------------------------------------------
# View listino (unificata) + Fallback tabelle
# ------------------------------------------------------------
def _get_all_listino_rows() -> List[Dict[str, Any]]:
    """
    Ritorna TUTTE le righe del Listino Accessori 3.0.

    Ordine di priorità:
    1) View vw_accessori_listino_completo (se esiste)
    2) View vw_accessori_listino (nome alternativo, se esiste)
    3) Fallback: unione delle tabelle codici (morsetti / catena_g8 / tycan)
       con aggiunta della colonna 'sorgente'.

    In questo modo l'API NON dipende rigidamente dalle VIEW:
    se lo script SQL non è stato ancora eseguito, si appoggia
    comunque ai dati reali presenti nelle tabelle.
    """
    # --- 1) Tentativo con view "completa" --------------------
    con = _get_connection()
    try:
        try:
            cur = con.execute("SELECT * FROM vw_accessori_listino_completo")
            rows = cur.fetchall()
            if rows:
                return _rows_to_dicts(rows)
        except sqlite3.OperationalError:
            # View mancante o non ancora creata → provo nome alternativo
            pass

        # --- 2) Tentativo con view alternativa ----------------
        try:
            cur = con.execute("SELECT * FROM vw_accessori_listino")
            rows = cur.fetchall()
            if rows:
                return _rows_to_dicts(rows)
        except sqlite3.OperationalError:
            # Nessuna view disponibile → passeremo al fallback
            pass

    finally:
        con.close()

    # --- 3) Fallback: unione tabelle codici ------------------
    morsetti = get_morsetti()
    for r in morsetti:
        r.setdefault("sorgente", "MORSETTI")

    catena = get_catena_g8()
    for r in catena:
        r.setdefault("sorgente", "CATENA_G8")

    tycan = get_tycan()
    for r in tycan:
        r.setdefault("sorgente", "TYCAN")

    combined: List[Dict[str, Any]] = []
    combined.extend(morsetti)
    combined.extend(catena)
    combined.extend(tycan)

    if not combined:
        # Qui significa: niente view E niente tabelle codici.
        raise HTTPException(
            status_code=500,
            detail=(
                "Nessun dato accessori trovato: view assenti e tabelle codici vuote. "
                "Controlla import CSV accessori e/o script view."
            ),
        )

    return combined


def get_listino_overview() -> Dict[str, int]:
    """
    Piccola panoramica dei conteggi per API /overview.

    Usa sempre i conteggi dalle tabelle di base,
    e per totale_codici usa la vista/fallback unificata.
    """
    return {
        "famiglie": len(get_famiglie()),
        "morsetti": len(get_morsetti()),
        "catena_g8": len(get_catena_g8()),
        "tycan": len(get_tycan()),
        "totale_codici": len(_get_all_listino_rows()),
    }


# ------------------------------------------------------------
# Filtri e paginazione lato Python (robusti sui nomi colonne)
# ------------------------------------------------------------
def filter_listino(
    famiglia: Optional[str] = None,
    sorgente: Optional[str] = None,
    cerca: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Applica filtri "soft" su lista unificata.

    - famiglia: match case-insensitive su campo 'famiglia' se presente.
    - sorgente: match case-insensitive su colonna 'sorgente'
      (MORSETTI / CATENA_G8 / TYCAN).
    - cerca: match case-insensitive su concatenazione di tutti i valori
      (codice, descrizione, ecc.).
    """
    rows = _get_all_listino_rows()
    famiglia_norm = famiglia.lower() if famiglia else None
    sorgente_norm = sorgente.lower() if sorgente else None
    cerca_norm = cerca.lower() if cerca else None

    def _match(row: Dict[str, Any]) -> bool:
        # filtro famiglia se richiesto
        if famiglia_norm:
            fam_val = str(row.get("famiglia", "")).lower()
            if famiglia_norm not in fam_val:
                return False

        # filtro sorgente se richiesto (MORSETTI / CATENA_G8 / TYCAN)
        if sorgente_norm:
            src_val = str(row.get("sorgente", "")).lower()
            if sorgente_norm != src_val:
                return False

        # filtro cerca globale
        if cerca_norm:
            joined = " ".join(str(v) for v in row.values())
            if cerca_norm not in joined.lower():
                return False

        return True

    filtered = [r for r in rows if _match(r)]
    total = len(filtered)

    # paginazione
    start = max(offset, 0)
    end = start + max(limit, 0)
    page = filtered[start:end]

    return total, page


def search_by_code(codice: str) -> Optional[Dict[str, Any]]:
    """
    Cerca un codice in TUTTE le righe della vista/fallback unificata.

    Strategia:
    - lower-case del codice cercato
    - per ogni riga, controlla se qualche colonna stringa è esattamente uguale al codice
      (ignorando maiuscole/minuscole)
    - se trovato, ritorna la riga arricchita con 'source_table' := valore di 'sorgente'
    """
    target = codice.lower()
    rows = _get_all_listino_rows()

    for row in rows:
        for val in row.values():
            if isinstance(val, str) and val.lower() == target:
                result = dict(row)
                result["source_table"] = row.get("sorgente", "UNKNOWN")
                return result

    return None
