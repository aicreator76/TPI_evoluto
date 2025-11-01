import hashlib
from typing import Iterable, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert as sqlite_insert


def _fp(*parts: str) -> str:
    s = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:64]


def upsert_many(session: Session, model, rows: Iterable[dict]) -> Tuple[int, int, int]:
    inserted = updated = skipped = 0
    for r in rows:
        r = dict(r)
        r["fingerprint"] = _fp(
            r.get("codice"),
            r.get("descrizione"),
            r.get("categoria"),
            r.get("prezzo_eur"),
            r.get("url"),
        )
        stmt = sqlite_insert(model).values(r)
        stmt = stmt.on_conflict_do_update(
            index_elements=[model.codice],
            set_={
                "descrizione": stmt.excluded.descrizione,
                "categoria": stmt.excluded.categoria,
                "prezzo_eur": stmt.excluded.prezzo_eur,
                "url": stmt.excluded.url,
                "fingerprint": stmt.excluded.fingerprint,
            },
        )
        session.execute(stmt)
        current = session.get(model, r["codice"])
        if current and current.fingerprint == r["fingerprint"]:
            skipped += 1
        else:
            # best-effort: se esisteva prima -> updated, altrimenti inserted
            if current:
                updated += 1
            else:
                inserted += 1
    return inserted, updated, skipped
