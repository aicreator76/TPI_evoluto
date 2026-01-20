from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None  # Se zoneinfo non è disponibile, si userà date.today()

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
)

ALIASES: Dict[str, set[str]] = {
    "id_dpi": {"id_dpi", "id", "codice", "codice_dpi", "dpi_id"},
    "tipo": {"tipo", "type", "modello", "descrizione"},
    "marca": {"marca", "brand"},
    "matricola": {"matricola", "seriale", "serial", "sn"},
    "data_scadenza": {
        "data_scadenza",
        "scadenza",
        "expiry",
        "expiration",
        "data_fine",
        "data_scad",
    },
    "assegnato_a": {"assegnato_a", "assegnato", "user", "utente", "operatore", "dipendente"},
    "sede": {"sede", "site", "stabilimento", "luogo"},
    "note": {"note", "notes", "annotazioni"},
}


def norm_key(s: str) -> str:
    """Normalizza una chiave rimuovendo spazi e portando a minuscolo."""
    return (s or "").strip().lower().replace(" ", "_")


def map_columns(cols: List[str]) -> Dict[str, str]:
    """Mappa le colonne di input ai nomi canonici definiti in ALIASES."""
    src = [norm_key(c) for c in cols]
    mapping: Dict[str, str] = {}
    for canonical, alts in ALIASES.items():
        for c in src:
            if c in alts:
                mapping[canonical] = c
                break
    return mapping


def parse_date(v: Any) -> Optional[date]:
    """Parsa una data da varie rappresentazioni."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "")).date()
    except Exception:
        pass
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


def today_rome() -> date:
    """Restituisce la data odierna nel fuso Europe/Rome (fallback su date.today)."""
    if ZoneInfo is None:
        return date.today()
    try:
        return datetime.now(ZoneInfo("Europe/Rome")).date()
    except Exception:
        return date.today()


def status_from_days(days: int) -> str:
    """Classifica la scadenza in verde/giallo/rosso in base ai giorni residui."""
    if days < 0:
        return "rosso"
    if days <= 60:
        return "giallo"
    return "verde"


def load_csv(path: Path) -> List[Dict[str, Any]]:
    """Carica un file CSV in una lista di dict."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return [dict(row) for row in r]


def load_xlsx(path: Path) -> List[Dict[str, Any]]:
    """Carica un XLSX usando openpyxl; lancia errore se la libreria manca."""
    try:
        import openpyxl
    except Exception as e:
        raise RuntimeError(
            "openpyxl non installato: converti XLSX→CSV oppure installa: pip install openpyxl"
        ) from e

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    values = list(ws.values)
    if not values:
        return []
    headers = [str(x).strip() if x is not None else "" for x in values[0]]
    rows: List[Dict[str, Any]] = []
    for line in values[1:]:
        # converte il tuple in lista per indicizzazione sicura (mypy)
        line_values = list(line)
        row = {
            headers[i]: (line_values[i] if i < len(line_values) else None)
            for i in range(len(headers))
        }
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Percorso CSV o XLSX")
    parser.add_argument(
        "--out", default="E:\\CLONAZIONE\\tpi_evoluto\\reports", help="Cartella report"
    )
    parser.add_argument("--log", default="E:\\CLONAZIONE\\tpi_evoluto\\logs", help="Cartella log")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"[ERR] input not found: {inp}", file=sys.stderr)
        return 2

    stamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = Path(args.log)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / f"DPI_run_{stamp}.log"

    def log(msg: str) -> None:
        prev = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        log_path.write_text(prev + msg + "\n", encoding="utf-8")

    # Carica righe
    if inp.suffix.lower() == ".csv":
        rows = load_csv(inp)
    elif inp.suffix.lower() in {".xlsx", ".xlsm"}:
        rows = load_xlsx(inp)
    else:
        print("[ERR] unsupported input (use .csv .xlsx .xlsm)", file=sys.stderr)
        return 3

    if not rows:
        print("[ERR] input has 0 rows", file=sys.stderr)
        return 4

    mapping = map_columns(list(rows[0].keys()))
    if "data_scadenza" not in mapping:
        print(
            f"[ERR] missing expiry column. Found columns: {list(rows[0].keys())}", file=sys.stderr
        )
        return 5

    t0 = today_rome()
    out_rows: List[Dict[str, Any]] = []
    parse_errors = 0

    for r in rows:
        r_norm = {norm_key(k): v for k, v in r.items()}

        def get_value(key: str) -> Any:
            return r_norm.get(mapping.get(key, ""), None)

        exp = parse_date(get_value("data_scadenza"))
        if exp is None:
            parse_errors += 1
            continue

        days_to_expiry = (exp - t0).days
        out_rows.append(
            {
                "id_dpi": get_value("id_dpi") or "",
                "tipo": get_value("tipo") or "",
                "marca": get_value("marca") or "",
                "matricola": get_value("matricola") or "",
                "data_scadenza": exp.isoformat(),
                "assegnato_a": get_value("assegnato_a") or "",
                "sede": get_value("sede") or "",
                "note": get_value("note") or "",
                "days_to_expiry": days_to_expiry,
                "stato": status_from_days(days_to_expiry),
            }
        )

    # Categorie
    scaduti = [x for x in out_rows if x["days_to_expiry"] < 0]
    due30 = [x for x in out_rows if 0 <= x["days_to_expiry"] <= 30]
    due15 = [x for x in out_rows if 0 <= x["days_to_expiry"] <= 15]
    due1 = [x for x in out_rows if 0 <= x["days_to_expiry"] <= 1]

    report_csv = out_dir / f"DPI_Scadenze_{stamp}.csv"
    report_json = out_dir / f"DPI_Summary_{stamp}.json"
    payload_n8n = out_dir / f"n8n_payload_{stamp}.json"

    fields = (
        list(out_rows[0].keys())
        if out_rows
        else [
            "id_dpi",
            "data_scadenza",
            "days_to_expiry",
            "stato",
        ]
    )
    with report_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)

    summary = {
        "timestamp_utc": stamp,
        "today_rome": t0.isoformat(),
        "counts": {
            "tot": len(out_rows),
            "verde": sum(1 for x in out_rows if x["stato"] == "verde"),
            "giallo": sum(1 for x in out_rows if x["stato"] == "giallo"),
            "rosso": sum(1 for x in out_rows if x["stato"] == "rosso"),
            "parse_errors": parse_errors,
        },
        "thresholds": {
            "due_30": len(due30),
            "due_15": len(due15),
            "due_1": len(due1),
            "expired": len(scaduti),
        },
    }
    report_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    n8n_payload = {
        "meta": summary,
        "expired": scaduti,
        "due_30": due30,
        "due_15": due15,
        "due_1": due1,
    }
    payload_n8n.write_text(
        json.dumps(n8n_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    log(f"[OK] input={inp}")
    log(f"[OK] wrote={report_csv}")
    log(f"[OK] wrote={report_json}")
    log(f"[OK] wrote={payload_n8n}")
    log(f"[OK] counts={summary['counts']}")

    print(
        f"[OK] DPI report ready tot={summary['counts']['tot']} expired={len(scaduti)} due30={len(due30)}"
    )
    print(f"[OK] wrote {report_csv}")
    print(f"[OK] wrote {payload_n8n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
