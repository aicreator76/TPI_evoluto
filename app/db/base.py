"""
E:\CLONAZIONE\tpi_evoluto\app\db\base.py

Base SQLAlchemy condivisa per tutti i modelli TPI.

Obiettivo:
- Esporre una Base unica (SQLAlchemy 2.0 style).
- Popolare Base.metadata importando i modelli in modo idempotente (safe).
- Restare ruff-clean (niente import “in mezzo al file” -> niente E402).
"""

from __future__ import annotations

from importlib import import_module
from typing import Final

from sqlalchemy.orm import DeclarativeBase

_MODELS_PKG: Final[str] = "app.db.models"
_models_loaded: bool = False


class Base(DeclarativeBase):
    """Base SQLAlchemy condivisa per tutti i modelli TPI."""


def load_models() -> None:
    """
    Importa il package dei modelli per registrare le tabelle su Base.metadata.

    - Idempotente: chiamala quante volte vuoi.
    - Utile in startup FastAPI / script / test.
    """
    global _models_loaded
    if _models_loaded:
        return
    import_module(_MODELS_PKG)
    _models_loaded = True


# Compatibilità/operatività: autocarica i modelli all'import della Base
# (così Base.metadata è già popolata quando serve).
load_models()
