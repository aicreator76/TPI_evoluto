from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Literal

from fastapi import APIRouter, HTTPException

# ==================================================
#  ROUTER FUNI IN FIBRA – API UFFICIALE TPI
# ==================================================
router = APIRouter(
    prefix="/api/funi-fibra",
    tags=["funi_fibra"],
)

# --------------------------------------------------
# PERCORSI COMPLETI (WIN / TUA MACCHINA)
# --------------------------------------------------
# Radice progetto TPI_evoluto
PROJECT_ROOT: Path = Path(r"E:\CLONAZIONE\tpi_evoluto")

# Cartella dati funi in fibra
DATA_DIR: Path = PROJECT_ROOT / "data" / "cataloghi" / "funi_fibra"

MASTER_CSV: Path = DATA_DIR / "master" / "funi_fibra_master.csv"
MASTER_JSON: Path = DATA_DIR / "master" / "funi_fibra_items.json"

FuniRecord = Dict[str, Any]


# --------------------------------------------------
# Helpers lettura / normalizzazione
# --------------------------------------------------
def _normalize_record(row: Dict[str, Any]) -> FuniRecord:
    """
    Normalizza un record funi_fibra:
    - scadenza vuota → None
    - trim stringhe base
    """
    rec: FuniRecord = dict(row)

    # Normalizzo scadenza
    if not rec.get("scadenza"):
        rec["scadenza"] = None

    # Pulizia leggera di alcune chiavi testuali principali
    for key in ("id_tpi", "codice", "codice_fabbrica", "famiglia", "linea"):
        if key in rec and isinstance(rec[key], str):
            rec[key] = rec[key].strip()

    return rec


def _load_master() -> List[FuniRecord]:
    """
    Ritorna tutte le famiglie funi_fibra dal master.

    Usa prima il JSON (se presente), altrimenti il CSV.
    Percorsi fissi su E:\\CLONAZIONE\\tpi_evoluto\\...
    """
    # Preferisco JSON se esiste (più veloce e già strutturato)
    if MASTER_JSON.exists():
        with MASTER_JSON.open("r", encoding="utf-8") as f:
            items = json.load(f)

        return [_normalize_record(row) for row in items]

    # Fallback su CSV master
    if not MASTER_CSV.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Master funi_fibra non trovato ({MASTER_CSV})",
        )

    rows: List[FuniRecord] = []
    with MASTER_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(_normalize_record(r))

    return rows


def _csv_path_for_care(care: str) -> Path:
    """
    Ritorna il path completo del CSV per la care specifica.
    Es. forestale → E:\\CLONAZIONE\\tpi_evoluto\\data\\cataloghi\\funi_fibra\\forestale\\funi_fibra_forestale.csv
    """
    return DATA_DIR / care / f"funi_fibra_{care}.csv"


def _load_care(
    care: Literal["forestale", "sollevamento", "industriale"],
) -> List[FuniRecord]:
    """
    Carica il CSV specifico della care (forestale / sollevamento / industriale)
    usando i percorsi completi.
    """
    path = _csv_path_for_care(care)
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"CSV funi_fibra per care '{care}' non trovato ({path})",
        )

    rows: List[FuniRecord] = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(_normalize_record(r))

    return rows


# --------------------------------------------------
# Endpoint overview (per cruscotto e check rapidi)
# --------------------------------------------------
@router.get("/", name="funi_fibra_overview")
def funi_fibra_overview() -> Dict[str, Any]:
    """
    Ritorna solo i conteggi per care.
    Utile come cruscotto rapido lato API.
    """
    result: Dict[str, int] = {}
    for care in ("forestale", "sollevamento", "industriale"):
        try:
            items = _load_care(care)  # type: ignore[arg-type]
            result[care] = len(items)
        except HTTPException:
            result[care] = 0

    return {"care_counts": result}


# --------------------------------------------------
# Endpoint per-care (forestale / sollevamento / industriale)
# --------------------------------------------------
@router.get("/forestale", name="funi_fibra_forestale")
def funi_fibra_forestale() -> Dict[str, Any]:
    """
    Restituisce tutte le famiglie funi_fibra per la care FORESTALE.
    """
    items = _load_care("forestale")
    return {
        "care": "forestale",
        "count": len(items),
        "items": items,
    }


@router.get("/sollevamento", name="funi_fibra_sollevamento")
def funi_fibra_sollevamento() -> Dict[str, Any]:
    """
    Restituisce tutte le famiglie funi_fibra per la care SOLLEVAMENTO.
    """
    items = _load_care("sollevamento")
    return {
        "care": "sollevamento",
        "count": len(items),
        "items": items,
    }


@router.get("/industriale", name="funi_fibra_industriale")
def funi_fibra_industriale() -> Dict[str, Any]:
    """
    Restituisce tutte le famiglie funi_fibra per la care INDUSTRIALE.
    """
    items = _load_care("industriale")
    return {
        "care": "industriale",
        "count": len(items),
        "items": items,
    }


# --------------------------------------------------
# Endpoint “ALL” per n8n / sync esterni
# --------------------------------------------------
@router.get("/all", name="funi_fibra_all")
def funi_fibra_all() -> Dict[str, Any]:
    """
    Ritorna TUTTE le famiglie funi_fibra in un colpo solo.

    Perfetto per:
    - sync verso DB / Google Sheets
    - costruire dropdown di scelta nei flow n8n
    """
    items = _load_master()
    return {
        "count": len(items),
        "items": items,
    }


# --------------------------------------------------
# Lookup per codice (FOREST-IND-0001, ecc.)
# --------------------------------------------------
@router.get("/by-code/{codice}", name="funi_fibra_by_code")
def funi_fibra_by_code(codice: str) -> Dict[str, Any]:
    """
    Ricerca una singola famiglia per 'codice' (es. FOREST-IND-0001).

    Matching case-insensitive su più chiavi possibili:
    - 'codice'
    - 'id_tpi'
    - 'codice_fabbrica'
    """
    codice_norm = codice.strip().lower()
    if not codice_norm:
        raise HTTPException(status_code=400, detail="Codice vuoto o non valido")

    items = _load_master()
    search_keys = ("codice", "id_tpi", "codice_fabbrica")

    for row in items:
        for key in search_keys:
            value = str(row.get(key, "")).strip().lower()
            if value and value == codice_norm:
                return {
                    "found": True,
                    "match_key": key,
                    "item": row,
                }

    raise HTTPException(
        status_code=404,
        detail=f"Nessuna famiglia funi_fibra trovata per codice '{codice}'",
    )
