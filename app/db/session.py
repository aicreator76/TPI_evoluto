from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _build_database_url() -> str:
    url = os.getenv("DATABASE_URL") or os.getenv("SQLALCHEMY_DATABASE_URL")
    if url:
        return url
    # default locale (repo root)
    return "sqlite:///./tpi_evoluto.sqlite"


DATABASE_URL = _build_database_url()

connect_args: dict[str, object] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


@contextmanager
def db_session() -> Iterator[Session]:
    """Context manager: apre Session, commit automatico, rollback su errore."""
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Crea tabelle (DEV). Nota: non fa migrazioni/ALTER su tabelle già esistenti."""
    import app.db.models  # noqa: F401 (registra i modelli in Base.metadata)
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """Dependency FastAPI."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["DATABASE_URL", "engine", "SessionLocal", "db_session", "init_db", "get_db"]
