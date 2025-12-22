"""
Router FastAPI per Listino 3.0 Accessori.

Path base: /api/accessori

Endpoint principali:
- GET /api/accessori/overview
- GET /api/accessori/listino
- GET /api/accessori/listino/filtrato
- GET /api/accessori/listino/export
- GET /api/accessori/listino/by-code/{codice}
- GET /api/accessori/famiglie
- GET /api/accessori/morsetti
- GET /api/accessori/catena-g8
- GET /api/accessori/tycan
"""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from app.db.accessori_db import (
    DB_PATH,
    filter_listino,
    get_catena_g8,
    get_famiglie,
    get_listino_overview,
    get_morsetti,
    get_tycan,
    search_by_code,
)

# Prefix UNICO: /api/accessori
router = APIRouter(
    prefix="/api/accessori",
    tags=["Accessori 3.0"],
)


def _json_not_found(codice: str) -> JSONResponse:
    """Contratto 404 auditabile: found=false."""
    return JSONResponse(
        status_code=404,
        content={
            "found": False,
            "code": codice,
            "item": None,
            "detail": f"Codice non trovato nel listino accessori: {codice}",
        },
    )


def _json_bad_request(codice: str) -> JSONResponse:
    """Contratto 400 coerente: found=false + detail."""
    return JSONResponse(
        status_code=400,
        content={
            "found": False,
            "code": codice,
            "item": None,
            "detail": "Codice non valido",
        },
    )


# ------------------------------------------------------------
# Overview
# ------------------------------------------------------------
@router.get("/overview", name="accessori_overview")
def accessori_overview() -> Dict[str, Any]:
    """
    Ritorna una panoramica di base sul blocco accessori.

    - Conteggi righe
    - Percorso DB
    """
    overview = get_listino_overview()
    return {
        "source_db": str(DB_PATH),
        "summary": overview,
    }


# ------------------------------------------------------------
# Famiglie e codici di base
# ------------------------------------------------------------
@router.get("/famiglie", name="accessori_famiglie")
def list_famiglie() -> Dict[str, Any]:
    """Ritorna l'elenco famiglie accessori."""
    items = get_famiglie()
    return {
        "source_db": str(DB_PATH),
        "total": len(items),
        "items": items,
    }


@router.get("/morsetti", name="accessori_morsetti")
def list_morsetti() -> Dict[str, Any]:
    """Ritorna elenco codici morsetti."""
    items = get_morsetti()
    return {
        "source_db": str(DB_PATH),
        "total": len(items),
        "items": items,
    }


@router.get("/catena-g8", name="accessori_catena_g8")
def list_catena_g8() -> Dict[str, Any]:
    """Ritorna elenco codici catena G8."""
    items = get_catena_g8()
    return {
        "source_db": str(DB_PATH),
        "total": len(items),
        "items": items,
    }


@router.get("/tycan", name="accessori_tycan")
def list_tycan() -> Dict[str, Any]:
    """Ritorna elenco codici Tycan."""
    items = get_tycan()
    return {
        "source_db": str(DB_PATH),
        "total": len(items),
        "items": items,
    }


# ------------------------------------------------------------
# Listino completo + filtri
# ------------------------------------------------------------
@router.get("/listino", name="accessori_listino")
def listino_accessori(
    famiglia: Optional[str] = Query(None),
    sorgente: Optional[str] = Query(None),
    cerca: Optional[str] = Query(None),
    limit: int = Query(100, ge=0, le=5000),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """
    Listino 3.0 Accessori (alias di /listino/filtrato).

    Se non passi filtri, ritorna tutti i codici (paginati).
    """
    total, items = filter_listino(
        famiglia=famiglia,
        sorgente=sorgente,
        cerca=cerca,
        limit=limit,
        offset=offset,
    )
    return {
        "source_db": str(DB_PATH),
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


@router.get("/listino/filtrato", name="accessori_listino_filtrato")
def listino_accessori_filtrato(
    famiglia: Optional[str] = Query(None),
    sorgente: Optional[str] = Query(None),
    cerca: Optional[str] = Query(None),
    limit: int = Query(100, ge=0, le=5000),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """
    Versione esplicita filtrabile del listino.

    Parametri identici a /listino.
    """
    total, items = filter_listino(
        famiglia=famiglia,
        sorgente=sorgente,
        cerca=cerca,
        limit=limit,
        offset=offset,
    )
    return {
        "source_db": str(DB_PATH),
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


# ------------------------------------------------------------
# Ricerca per codice
# ------------------------------------------------------------
@router.get(
    "/listino/by-code/{codice}",
    name="accessori_listino_by_code",
    responses={
        200: {
            "description": "Codice trovato",
            "content": {
                "application/json": {
                    "example": {
                        "source_db": "...",
                        "found": True,
                        "item": {},
                        "source_table": "MORSETTI",
                    }
                }
            },
        },
        404: {
            "description": "Codice non trovato (audit)",
            "content": {
                "application/json": {
                    "example": {
                        "found": False,
                        "code": "ABC123",
                        "item": None,
                        "detail": "Codice non trovato nel listino accessori: ABC123",
                    }
                }
            },
        },
    },
)
def listino_by_code(codice: str) -> Any:
    """
    Ricerca un singolo codice nel listino unificato.

    Contratto:
    - 200 -> {found:true, item:...}
    - 404 -> {found:false, code:"...", item:null, detail:"..."}
    """
    if not codice or not codice.strip():
        return _json_bad_request(codice)

    item = search_by_code(codice)
    if not item:
        return _json_not_found(codice)

    return {
        "source_db": str(DB_PATH),
        "found": True,
        "item": item,
        "source_table": item.get("source_table", "UNKNOWN"),
    }


# ------------------------------------------------------------
# Export CSV
# ------------------------------------------------------------
@router.get(
    "/listino/export",
    name="accessori_listino_export",
)
def export_listino_csv(
    famiglia: Optional[str] = Query(None),
    sorgente: Optional[str] = Query(None),
    cerca: Optional[str] = Query(None),
    limit: int = Query(5000, ge=0, le=20000),
    offset: int = Query(0, ge=0),
) -> Response:
    """
    Esporta il listino (eventualmente filtrato) in CSV.

    - Separatore: ;
    - UTF-8
    - Allegato scaricabile (Content-Disposition)
    """
    _total, items = filter_listino(
        famiglia=famiglia,
        sorgente=sorgente,
        cerca=cerca,
        limit=limit,
        offset=offset,
    )

    csv_buf = io.StringIO(newline="")  # evita righe vuote su Windows

    if not items:
        w = csv.writer(csv_buf, delimiter=";")
        w.writerow(["message"])
        w.writerow(["Nessun dato nel listino (filtri troppo restrittivi?)"])
    else:
        fieldnames: List[str] = list(items[0].keys())
        dw = csv.DictWriter(
            csv_buf,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        dw.writeheader()
        for row in items:
            dw.writerow(row)

    content = csv_buf.getvalue()

    filename = "TPI_ACCESSORI_LISTINO_3_0_2025-12-08.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return Response(
        content,
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )
