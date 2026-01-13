from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

DEFAULT_LOCK_NAME = "orchestrator0"


@dataclass(frozen=True)
class LockState:
    name: str
    exists: bool
    locked: bool
    owner: str | None
    token: str | None
    locked_until: datetime | None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_dt(v: Any) -> datetime | None:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.replace(tzinfo=timezone.utc) if v.tzinfo is None else v.astimezone(timezone.utc)
    if isinstance(v, str):
        s = v.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(s)
            return (
                dt.replace(tzinfo=timezone.utc)
                if dt.tzinfo is None
                else dt.astimezone(timezone.utc)
            )
        except Exception:
            return None
    return None


def lock_status(db: Session, name: str) -> LockState:
    row = db.execute(
        text(
            """
            SELECT name, locked_until, owner, token
            FROM orchestrator_locks
            WHERE name=:name
            """
        ),
        {"name": name},
    ).first()

    if not row:
        return LockState(
            name=name, exists=False, locked=False, owner=None, token=None, locked_until=None
        )

    locked_until = _coerce_dt(row[1])
    now = _utcnow()
    locked = bool(locked_until and locked_until > now)

    return LockState(
        name=str(row[0]),
        exists=True,
        locked=locked,
        owner=cast(str | None, row[2]),
        token=cast(str | None, row[3]),
        locked_until=locked_until,
    )


def acquire_lock(db: Session, name: str, ttl_seconds: int, owner: str) -> tuple[bool, LockState]:
    """
    Lease lock DB:
      - INSERT se manca
      - UPDATE se scaduto
      - altrimenti fail (409 lato API)
    """
    now = _utcnow()
    until = now + timedelta(seconds=int(ttl_seconds))
    token = secrets.token_hex(16)

    dialect = db.get_bind().dialect.name
    params = {"name": name, "until": until, "owner": owner, "token": token, "now": now}

    try:
        if dialect == "sqlite":
            res_ins = cast(
                CursorResult[Any],
                db.execute(
                    text(
                        """
                        INSERT OR IGNORE INTO orchestrator_locks
                        (name, locked_until, owner, token, created_at, updated_at)
                        VALUES (:name, :until, :owner, :token, :now, :now)
                        """
                    ),
                    params,
                ),
            )
            if res_ins.rowcount == 1:
                db.commit()
                return True, lock_status(db, name)

            res_upd = cast(
                CursorResult[Any],
                db.execute(
                    text(
                        """
                        UPDATE orchestrator_locks
                        SET locked_until=:until, owner=:owner, token=:token, updated_at=:now
                        WHERE name=:name AND locked_until <= :now
                        """
                    ),
                    params,
                ),
            )
            if res_upd.rowcount == 1:
                db.commit()
                return True, lock_status(db, name)

            db.rollback()
            return False, lock_status(db, name)

        # Postgres / altri
        res_ins = cast(
            CursorResult[Any],
            db.execute(
                text(
                    """
                    INSERT INTO orchestrator_locks
                    (name, locked_until, owner, token, created_at, updated_at)
                    VALUES (:name, :until, :owner, :token, :now, :now)
                    ON CONFLICT (name) DO NOTHING
                    """
                ),
                params,
            ),
        )
        if res_ins.rowcount == 1:
            db.commit()
            return True, lock_status(db, name)

        res_upd = cast(
            CursorResult[Any],
            db.execute(
                text(
                    """
                    UPDATE orchestrator_locks
                    SET locked_until=:until, owner=:owner, token=:token, updated_at=:now
                    WHERE name=:name AND locked_until <= :now
                    """
                ),
                params,
            ),
        )
        if res_upd.rowcount == 1:
            db.commit()
            return True, lock_status(db, name)

        db.rollback()
        return False, lock_status(db, name)

    except Exception:
        db.rollback()
        raise


def release_lock(db: Session, name: str, token: str) -> bool:
    now = _utcnow()
    res = cast(
        CursorResult[Any],
        db.execute(
            text(
                """
                UPDATE orchestrator_locks
                SET locked_until=:now, updated_at=:now
                WHERE name=:name AND token=:token
                """
            ),
            {"name": name, "token": token, "now": now},
        ),
    )
    if res.rowcount == 1:
        db.commit()
        return True
    db.rollback()
    return False


__all__ = [
    "DEFAULT_LOCK_NAME",
    "LockState",
    "lock_status",
    "acquire_lock",
    "release_lock",
]
