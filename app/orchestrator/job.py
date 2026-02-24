from __future__ import annotations

import argparse
import csv
import json
import logging
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Iterator

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.orchestrator_models.orchestrator_event import OrchestratorEvent
from app.db.session import db_session, init_db

LOG = logging.getLogger("orchestrator0")


@dataclass(frozen=True)
class SourceRow:
    tenant: str
    ref_type: str  # "dpi" | "impianto" | "altro"
    ref_id: str
    expiry_date: date
    payload: dict[str, Any]


def _setup_logging(verbose: bool) -> None:
    # UTC in log (vendibile: log coerenti)
    logging.Formatter.converter = time.gmtime
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)sZ %(levelname)s %(name)s - %(message)s")


def _parse_date(s: str) -> date:
    s = (s or "").strip()
    if not s:
        raise ValueError("Empty date")

    # ISO date / ISO datetime
    try:
        if "T" in s or " " in s:
            s2 = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s2).date()
        return date.fromisoformat(s)
    except ValueError:
        pass

    # dd/mm/yyyy or dd/mm/yy
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Bad date: {s!r}")


def _sniff_dialect(sample: str) -> csv.Dialect:
    """
    mypy-safe:
    - typeshed puÃ² tipizzare sniff() come type[Dialect]
    - normalizziamo sempre a ISTANZA csv.Dialect
    """
    try:
        d: Any = csv.Sniffer().sniff(sample, delimiters=";,|\t")
    except Exception:
        return csv.excel()

    if isinstance(d, type):
        return d()
    return d


def _norm_row(row: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in (row or {}).items():
        if k is None:
            continue
        kk = str(k).strip().lower()
        if not kk:
            continue
        out[kk] = "" if v is None else str(v).strip()
    return out


def read_csv(path: Path, default_ref_type: str) -> Iterator[SourceRow]:
    """
    CSV robusto:
    - delimiter sniff (comma/semicolon/tab/pipe)
    - headers case-insensitive
    - supporta colonne alternative (tenant/ref_id/scadenza)
    """
    if not path.exists():
        raise FileNotFoundError(str(path))

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)

        dialect = _sniff_dialect(sample)
        reader = csv.DictReader(f, dialect=dialect)

        for row in reader:
            r = _norm_row(row)

            tenant = (
                r.get("tenant")
                or r.get("cliente")
                or r.get("company")
                or r.get("azienda")
                or r.get("tenant_id")
                or ""
            ).strip()

            ref_type = (
                (r.get("ref_type") or r.get("type") or default_ref_type or "").strip().lower()
            )

            ref_id = (
                r.get("ref")
                or r.get("ref_id")
                or r.get("refid")
                or r.get("id")
                or r.get("codice")
                or r.get("code")
                or r.get("sku")
                or r.get("serial")
                or r.get("asset_id")
                or ""
            ).strip()

            sca = (
                r.get("scadenza")
                or r.get("expiry_date")
                or r.get("expiry")
                or r.get("valid_to")
                or r.get("due_date")
                or ""
            ).strip()

            if not tenant or not ref_id or not sca:
                continue

            try:
                expiry = _parse_date(sca)
            except Exception as e:
                LOG.warning(
                    "Skip row (bad date) tenant=%s ref_id=%s scadenza=%r err=%s",
                    tenant,
                    ref_id,
                    sca,
                    e,
                )
                continue

            payload: dict[str, Any] = dict(row or {})
            yield SourceRow(
                tenant=tenant,
                ref_type=ref_type or default_ref_type,
                ref_id=ref_id,
                expiry_date=expiry,
                payload=payload,
            )


def _load_existing_keys(
    db: Session,
    tenants: set[str],
    ref_types: set[str],
    thresholds: list[int],
    start_date: date,
    end_date: date,
) -> set[tuple[str, str, str, int, date]]:
    if not tenants:
        return set()

    q = (
        select(
            OrchestratorEvent.tenant,
            OrchestratorEvent.ref_type,
            OrchestratorEvent.ref_id,
            OrchestratorEvent.threshold_days,
            OrchestratorEvent.event_date,
        )
        .where(OrchestratorEvent.tenant.in_(sorted(tenants)))
        .where(OrchestratorEvent.ref_type.in_(sorted(ref_types)))
        .where(OrchestratorEvent.threshold_days.in_(thresholds))
        .where(
            and_(
                OrchestratorEvent.event_date >= start_date, OrchestratorEvent.event_date <= end_date
            )
        )
    )

    existing: set[tuple[str, str, str, int, date]] = set()
    for t, rt, rid, th, ed in db.execute(q).all():
        existing.add((t, rt, rid, int(th), ed))
    return existing


def generate(
    db: Session,
    items: Iterable[SourceRow],
    thresholds: list[int],
    horizon_days: int,
    backfill_days: int,
    dry_run: bool,
) -> dict[str, int]:
    today = date.today()
    horizon = today + timedelta(days=horizon_days)
    backfill = today - timedelta(days=backfill_days)

    candidates: list[tuple[SourceRow, int, date]] = []
    tenants: set[str] = set()
    ref_types: set[str] = set()

    invalid = 0
    for it in items:
        tenants.add(it.tenant)
        ref_types.add(it.ref_type)

        for th in thresholds:
            try:
                event_date = it.expiry_date - timedelta(days=th)
            except Exception:
                invalid += 1
                continue

            if not (backfill <= event_date <= horizon):
                continue

            candidates.append((it, th, event_date))

    existing = _load_existing_keys(
        db=db,
        tenants=tenants,
        ref_types=ref_types,
        thresholds=thresholds,
        start_date=backfill,
        end_date=horizon,
    )

    created = 0
    skipped_existing = 0

    for it, th, event_date in candidates:
        key = (it.tenant, it.ref_type, it.ref_id, th, event_date)
        if key in existing:
            skipped_existing += 1
            continue

        ev = OrchestratorEvent(
            tenant=it.tenant,
            ref_type=it.ref_type,
            ref_id=it.ref_id,
            threshold_days=th,
            event_date=event_date,
            status=OrchestratorEvent.STATUS_PENDING,
        )

        payload: dict[str, Any] = dict(it.payload)
        payload.update(
            {
                "tenant": it.tenant,
                "ref_type": it.ref_type,
                "ref_id": it.ref_id,
                "expiry_date": it.expiry_date.isoformat(),
                "threshold_days": th,
                "event_date": event_date.isoformat(),
            }
        )
        ev.set_payload(payload)

        created += 1
        if not dry_run:
            db.add(ev)

        existing.add(key)

    if not dry_run:
        db.commit()

    return {
        "created": created,
        "skipped_existing": skipped_existing,
        "invalid": invalid,
        "candidates": len(candidates),
    }


def _parse_thresholds(raw: str) -> list[int]:
    xs: list[int] = []
    for x in (raw or "").split(","):
        x = x.strip()
        if not x:
            continue
        n = int(x)
        if n < 0:
            raise ValueError("thresholds must be >= 0")
        xs.append(n)
    return xs or [30, 15, 1]


def main() -> int:
    ap = argparse.ArgumentParser(prog="orchestrator0")
    ap.add_argument("--init-db", action="store_true")
    ap.add_argument("--dpi-csv", type=str)
    ap.add_argument("--impianti-csv", type=str)
    ap.add_argument("--horizon-days", type=int, default=31)
    ap.add_argument("--backfill-days", type=int, default=2)
    ap.add_argument("--thresholds", type=str, default="30,15,1")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", action="store_true", help="stampa summary in JSON (utile per n8n/CI)")
    args = ap.parse_args()

    _setup_logging(args.verbose)
    thresholds = _parse_thresholds(args.thresholds)

    if args.horizon_days < 0 or args.backfill_days < 0:
        raise SystemExit("horizon-days/backfill-days must be >= 0")

    if args.init_db:
        init_db()

    rows: list[SourceRow] = []
    if args.dpi_csv:
        rows.extend(list(read_csv(Path(args.dpi_csv), "dpi")))
    if args.impianti_csv:
        rows.extend(list(read_csv(Path(args.impianti_csv), "impianto")))

    if not rows:
        print("No input rows. Provide --dpi-csv and/or --impianti-csv")
        return 2

    with db_session() as db:
        summary = generate(
            db=db,
            items=rows,
            thresholds=thresholds,
            horizon_days=args.horizon_days,
            backfill_days=args.backfill_days,
            dry_run=args.dry_run,
        )

    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        prefix = "DRYRUN: would create " if args.dry_run else "Created "
        print(
            prefix + f"{summary['created']} events "
            f"(candidates={summary['candidates']} skipped_existing={summary['skipped_existing']} invalid={summary['invalid']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
