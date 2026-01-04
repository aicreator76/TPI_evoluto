"""
E:\\CLONAZIONE\\tpi_evoluto\\app\\db\\base.py

Base SQLAlchemy condivisa per tutti i modelli TPI.

Obiettivi:
- Definire una DeclarativeBase unica (SQLAlchemy 2.x).
- Impostare naming_convention utile per migrazioni/Alembic.
- Autocaricare i modelli (opzionale) per popolare Base.metadata.tables
  senza import manuali sparsi nel progetto.

Nota:
- Puoi disattivare l'autoload impostando:
  TPI_DB_AUTOIMPORT_MODELS=0
"""

from __future__ import annotations

import os
from importlib import import_module

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Naming convention consigliata (aiuta Alembic e vincoli coerenti)
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base SQLAlchemy condivisa per tutti i modelli TPI."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _should_autoload_models() -> bool:
    v = os.getenv("TPI_DB_AUTOIMPORT_MODELS", "1").strip().lower()
    return v not in {"0", "false", "no", "off"}


def autoload_models() -> None:
    """
    Importa il package dei modelli per registrare le tabelle su Base.metadata.

    Import locale + import_module per:
    - evitare E402 (import fuori posto)
    - ridurre rischi di circular import
    """
    # Il package app.db.models deve importare i moduli dei modelli (side-effect).
    import_module("app.db.models")


# Autoload di default (disattivabile via env var)
if _should_autoload_models():
    autoload_models()
