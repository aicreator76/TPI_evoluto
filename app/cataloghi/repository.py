from sqlalchemy import select


def upsert_many(session, Model, rows):
    # Colonne valide nel modello
    cols = {c.name for c in Model.__table__.c}
    key = "codice"

    clean_rows = []
    for r in rows:
        if key not in r or not r[key]:
            continue
        clean_rows.append({k: r.get(k) for k in cols if k in r})

    inserted = updated = skipped = 0
    for r in clean_rows:
        existing = session.execute(
            select(Model).where(getattr(Model, key) == r[key])
        ).scalar_one_or_none()

        if existing is None:
            session.add(Model(**r))
            inserted += 1
        else:
            changed = False
            for k in cols - {"id"}:
                new_val = r.get(k, getattr(existing, k))
                if getattr(existing, k) != new_val:
                    setattr(existing, k, new_val)
                    changed = True
            if changed:
                updated += 1
            else:
                skipped += 1

    session.commit()
    return inserted, updated, skipped
