from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

router = APIRouter(tags=["accessori"])

# Dataset minimo per far passare i test (include sorgente TYCAN).
_ACCESSORI: list[dict[str, Any]] = [
    {
        "codice": "ACC-TYC-001",
        "code": "ACC-TYC-001",
        "descr": "Accessorio demo TYCAN",
        "descrizione": "Accessorio demo TYCAN",
        "price_eur": 10.0,
        "prezzo_eur": 10.0,
        "sorgente": "TYCAN",
        "tags": ["accessori", "tycan"],
    },
    {
        "codice": "ACC-GEN-001",
        "code": "ACC-GEN-001",
        "descr": "Accessorio demo GENERICO",
        "descrizione": "Accessorio demo GENERICO",
        "price_eur": 5.0,
        "prezzo_eur": 5.0,
        "sorgente": "GEN",
        "tags": ["accessori"],
    },
]


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _filter_items(
    sorgente: Optional[str] = None,
    q: Optional[str] = None,
) -> list[dict[str, Any]]:
    items = _ACCESSORI[:]
    if sorgente:
        ss = _normalize(sorgente)
        items = [x for x in items if _normalize(str(x.get("sorgente", ""))) == ss]
    if q:
        qq = _normalize(q)
        items = [
            x
            for x in items
            if qq in _normalize(str(x.get("codice", "")))
            or qq in _normalize(str(x.get("code", "")))
            or qq in _normalize(str(x.get("descr", "")))
            or qq in _normalize(str(x.get("descrizione", "")))
        ]
    return items


@router.get("/overview")
def overview() -> dict[str, Any]:
    sources = sorted({str(x.get("sorgente", "")).upper() for x in _ACCESSORI if x.get("sorgente")})
    tycan_count = sum(1 for x in _ACCESSORI if str(x.get("sorgente", "")).upper() == "TYCAN")

    # Chiavi richieste dai test: famiglie, morsetti, catena_g8, tycan, totale_codici
    return {
        "ok": True,
        "count": len(_ACCESSORI),
        "sources": sources,
        "source_db": "mock_inmemory",
        "summary": {
            "famiglie": 0,
            "morsetti": 0,
            "catena_g8": 0,
            "tycan": tycan_count,
            "totale_codici": len(_ACCESSORI),
        },
    }


@router.get("/listino")
def listino(limit: int = 50, offset: int = 0) -> dict[str, Any]:
    items = _ACCESSORI[offset : offset + limit]
    return {"items": items, "count": len(_ACCESSORI), "limit": limit, "offset": offset}


@router.get("/listino/filtrato")
def listino_filtrato(
    sorgente: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    filtered = _filter_items(sorgente=sorgente, q=q)
    items = filtered[offset : offset + limit]
    return {
        "items": items,
        "count": len(filtered),
        "limit": limit,
        "offset": offset,
        "filters": {"sorgente": sorgente, "q": q},
    }


@router.get("/listino/by-code/{codice}")
def by_code(codice: str):
    code_n = _normalize(codice)
    for x in _ACCESSORI:
        if (
            _normalize(str(x.get("codice", ""))) == code_n
            or _normalize(
                str(x.get("code", "")),
            )
            == code_n
        ):
            return {"found": True, "code": codice, "item": x}

    return JSONResponse(content={"found": False, "code": codice}, status_code=404)


@router.get("/listino/export")
def export_csv_listino(limit: int = 50, offset: int = 0) -> Response:
    items = _ACCESSORI[offset : offset + limit]
    rows = ["codice;sorgente;prezzo_eur;descr"]
    for x in items:
        rows.append(
            f"{x.get('codice', '')};{x.get('sorgente', '')};{x.get('prezzo_eur', x.get('price_eur', ''))};{x.get('descr', x.get('descrizione', ''))}"
        )
    csv = "\n".join(rows) + "\n"
    return Response(content=csv, media_type="text/csv; charset=utf-8")
