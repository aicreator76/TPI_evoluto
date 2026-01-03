"""
Agente0 – Step2
Obiettivo:
- leggere reports/agente0/normalized_dpi_import.csv (output Step1)
- assegnare categoria/stato/scadenze (regole Step2)
- generare dashboard + actions log in reports/agente0/

Nota: notifiche (n8n/email) nello Step3/Step4.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IN_CSV = ROOT / "reports" / "agente0" / "normalized_dpi_import.csv"
OUT_DIR = ROOT / "reports" / "agente0"

DAYS_WARNING = 60


def _parse_date(value: str) -> date | None:
    v = (value or "").strip()
    if not v:
        return None

    # prova ISO: YYYY-MM-DD
    try:
        return date.fromisoformat(v[:10])
    except Exception:
        pass

    # prova formati comuni: DD/MM/YYYY, DD-MM-YYYY
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(v[:10], fmt).date()
        except Exception:
            continue

    return None


def _pick_expiry(row: dict[str, str]) -> date | None:
    # prova chiavi plausibili (senza sapere ancora lo schema definitivo dello Step1)
    keys = (
        "scadenza",
        "data_scadenza",
        "expiry_date",
        "expiry",
        "next_review",
        "next_review_date",
        "prossima_revisione",
    )
    for k in keys:
        if k in row and row[k].strip():
            d = _parse_date(row[k])
            if d:
                return d
    return None


@dataclass(frozen=True)
class Status:
    label: str  # OK / IN_SCADENZA / SCADUTO / UNKNOWN
    days: int | None


def _status_from_expiry(expiry: date | None, today: date) -> Status:
    if not expiry:
        return Status("UNKNOWN", None)

    delta = (expiry - today).days
    if delta < 0:
        return Status("SCADUTO", delta)
    if delta <= DAYS_WARNING:
        return Status("IN_SCADENZA", delta)
    return Status("OK", delta)


def main() -> int:
    if not IN_CSV.exists():
        raise SystemExit(f"Missing input CSV: {IN_CSV}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    today = date.today()
    rows: list[dict[str, str]] = []

    with IN_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({k: (v or "") for k, v in r.items()})

    enriched: list[dict[str, Any]] = []
    counts = {"TOTAL": 0, "OK": 0, "IN_SCADENZA": 0, "SCADUTO": 0, "UNKNOWN": 0}
    by_family: dict[str, int] = {}

    for r in rows:
        counts["TOTAL"] += 1

        fam = (r.get("famiglia") or r.get("categoria") or "N/D").strip() or "N/D"
        by_family[fam] = by_family.get(fam, 0) + 1

        expiry = _pick_expiry(r)
        st = _status_from_expiry(expiry, today)
        counts[st.label] += 1

        enriched.append(
            {
                **r,
                "_expiry": expiry.isoformat() if expiry else "",
                "_status": st.label,
                "_days_to_expiry": st.days if st.days is not None else "",
            }
        )

    dashboard = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input": str(IN_CSV.relative_to(ROOT)),
        "counts": counts,
        "by_family": dict(sorted(by_family.items(), key=lambda x: (-x[1], x[0]))),
        "rules": {"warning_days": DAYS_WARNING},
    }

    (OUT_DIR / "step2_dashboard.json").write_text(
        json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    md = []
    md.append("# Agente0 — Step2 Dashboard\n")
    md.append(f"- Generato: `{dashboard['generated_at']}`\n")
    md.append(f"- Input: `{dashboard['input']}`\n")
    md.append("\n## Conteggi\n")
    md.append(
        f"- TOTAL: **{counts['TOTAL']}**\n"
        f"- OK: **{counts['OK']}**\n"
        f"- IN_SCADENZA (≤ {DAYS_WARNING}g): **{counts['IN_SCADENZA']}**\n"
        f"- SCADUTO: **{counts['SCADUTO']}**\n"
        f"- UNKNOWN: **{counts['UNKNOWN']}**\n"
    )
    md.append("\n## Per famiglia\n")
    for k, v in dashboard["by_family"].items():
        md.append(f"- {k}: **{v}**\n")

    (OUT_DIR / "step2_dashboard.md").write_text("".join(md), encoding="utf-8")

    # Actions CSV (stub utile per Step3/Step4)
    actions_path = OUT_DIR / "step2_actions.csv"
    with actions_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["codice", "famiglia", "status", "days_to_expiry", "action"])
        for r in enriched:
            code = (r.get("codice") or r.get("id") or "").strip()
            fam = (r.get("famiglia") or r.get("categoria") or "N/D").strip()
            status = str(r.get("_status", "UNKNOWN"))
            days = r.get("_days_to_expiry", "")
            action = "NONE"
            if status == "SCADUTO":
                action = "BLOCK_USE"
            elif status == "IN_SCADENZA":
                action = "WARN"
            w.writerow([code, fam, status, days, action])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
