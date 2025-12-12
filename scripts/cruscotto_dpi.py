from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


# Percorso CSV principale del catalogo DPI
BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "docs" / "catalogo" / "catalogo_tpi.csv"


@dataclass
class DpiItem:
    codice: str
    descrizione: str
    prezzo: str
    gruppo: str
    scadenza_raw: str
    giorni_residui: int | None


def parse_scadenza(raw: str) -> int | None:
    """Ritorna giorni alla scadenza (int) oppure None se la data è mancante/errata."""
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        d = datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None
    today = date.today()
    return (d - today).days


def carica_dpi() -> list[DpiItem]:
    items: list[DpiItem] = []
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV non trovato: {CSV_PATH}")

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codice = (row.get("codice") or "").strip()
            descrizione = (row.get("descrizione") or "").strip()
            prezzo = (row.get("prezzo") or "").strip()
            gruppo = (row.get("gruppo") or "").strip()
            scadenza_raw = (row.get("scadenza") or "").strip()

            giorni = parse_scadenza(scadenza_raw)

            items.append(
                DpiItem(
                    codice=codice,
                    descrizione=descrizione,
                    prezzo=prezzo,
                    gruppo=gruppo,
                    scadenza_raw=scadenza_raw,
                    giorni_residui=giorni,
                )
            )
    return items


def calcola_cruscotto(items: list[DpiItem]) -> dict:
    totale = len(items)
    ok = warning = scaduti = err_data = anomalie = 0

    for item in items:
        # data
        if item.giorni_residui is None:
            err_data += 1
        else:
            if item.giorni_residui < 0:
                scaduti += 1
            elif item.giorni_residui <= 30:
                warning += 1
            else:
                ok += 1

        # anomalie base (codice o gruppo mancanti)
        if not item.codice or not item.gruppo:
            anomalie += 1

    # calcolo semaforo
    if scaduti > 0 or err_data > 0:
        semaforo = "ROSSO"
    elif warning > 0:
        semaforo = "GIALLO"
    else:
        semaforo = "VERDE"

    return {
        "semaforo": semaforo,
        "totale": totale,
        "ok": ok,
        "warning": warning,
        "scaduti": scaduti,
        "anomalie": anomalie,
        "err_data": err_data,
    }


def stampa_cruscotto(stats: dict) -> None:
    from datetime import datetime

    print("Cruscotto DPI")
    print(f"Semaforo modulo DPI: {stats['semaforo']}")
    print()
    print(f"Ultimo aggiornamento: {datetime.now().isoformat(timespec='seconds')}")
    print()
    print(f"Totale DPI: {stats['totale']}")
    print(f"OK: {stats['ok']}")
    print(f"Warning (≤30gg): {stats['warning']}")
    print(f"Scaduti: {stats['scaduti']}")
    print(f"Anomalie: {stats['anomalie']}")
    print(f"Righe con errore data: {stats['err_data']}")


def main() -> None:
    items = carica_dpi()
    stats = calcola_cruscotto(items)
    stampa_cruscotto(stats)


if __name__ == "__main__":
    main()
