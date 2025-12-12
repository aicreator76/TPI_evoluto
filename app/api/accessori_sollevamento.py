from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from app.db.accessori import (
    find_accessorio_by_codice,
    get_accessori_overview,
    get_catena_g8_codici,
    get_famiglie_accessori,
    get_listino_full,
    get_morsetti_codici,
    get_tycan_codici,
)

# --------------------------------------------------
# Router ACCESSORI (DEV LIBERA: nessun token richiesto)
# --------------------------------------------------
router = APIRouter(
    prefix="/api/accessori",
    tags=["accessori"],
)


# --------------------------------------------------
# Overview – cruscotto rapido
# --------------------------------------------------
@router.get("/overview", name="accessori_overview")
def accessori_overview() -> Dict[str, Any]:
    """
    Cruscotto rapido ACCESSORI 3.0.

    Ritorna:
    - conteggi per tabella (famiglie, morsetti, catena_g8, tycan)
    - totale codici complessivo
    """
    counts = get_accessori_overview()
    total_codici = counts["morsetti"] + counts["catena_g8"] + counts["tycan"]

    return {
        "counts": counts,
        "total_codici": total_codici,
    }


# --------------------------------------------------
# Famiglie
# --------------------------------------------------
@router.get("/famiglie", name="accessori_famiglie")
def accessori_famiglie() -> Dict[str, Any]:
    """
    Ritorna tutte le famiglie accessori.
    """
    items = get_famiglie_accessori()
    return {
        "count": len(items),
        "items": items,
    }


# --------------------------------------------------
# Codici per tipologia
# --------------------------------------------------
@router.get("/morsetti", name="accessori_morsetti")
def accessori_morsetti() -> Dict[str, Any]:
    items = get_morsetti_codici()
    return {
        "tipo": "morsetti",
        "count": len(items),
        "items": items,
    }


@router.get("/catena-g8", name="accessori_catena_g8")
def accessori_catena_g8() -> Dict[str, Any]:
    items = get_catena_g8_codici()
    return {
        "tipo": "catena_g8",
        "count": len(items),
        "items": items,
    }


@router.get("/tycan", name="accessori_tycan")
def accessori_tycan() -> Dict[str, Any]:
    items = get_tycan_codici()
    return {
        "tipo": "tycan",
        "count": len(items),
        "items": items,
    }


# --------------------------------------------------
# Listino 3.0 – FULL
# --------------------------------------------------
@router.get("/listino", name="accessori_listino_full")
def accessori_listino_full() -> Dict[str, Any]:
    """
    Listino 3.0 ACCESSORI.

    Unisce tutti i codici (morsetti, catena G8, TYCAN) in un'unica lista.
    Ogni riga ha il campo 'sorgente' per capire da quale tabella proviene.
    """
    items = get_listino_full()
    return {
        "count": len(items),
        "items": items,
    }


# --------------------------------------------------
# Lookup per codice
# --------------------------------------------------
@router.get("/by-code/{codice}", name="accessori_by_code")
def accessori_by_code(codice: str) -> Dict[str, Any]:
    """
    Ricerca di un singolo codice accessorio (case-insensitive).

    Controlla automaticamente:
    - tpi_accessori_morsetti
    - tpi_accessori_catena_g8
    - tpi_accessori_tycan
    """
    item = find_accessorio_by_codice(codice)
    return {
        "found": True,
        "item": item,
    }
