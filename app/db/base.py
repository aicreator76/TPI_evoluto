from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base SQLAlchemy condivisa per tutti i modelli TPI."""


def load_all_models() -> None:
    # Importa i modelli per popolare Base.metadata (evita circular & ruff E402).
    import app.db.models  # noqa: F401
    import app.db.orchestrator_models.orchestrator_event  # noqa: F401
    import app.db.orchestrator_models.orchestrator_lock  # noqa: F401


load_all_models()
