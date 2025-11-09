from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI

"""
Genera docs/openapi.json a partire dalla FastAPI app principale di TPI_evoluto.
"""

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = PROJECT_ROOT / "docs" / "openapi.json"


def ensure_project_on_path() -> None:
    """Assicura che la root del progetto sia in sys.path."""
    root_str = str(PROJECT_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def load_app() -> FastAPI:
    """Carica l'istanza FastAPI `app` dal progetto.

    Ordine tentativi:
    1. app.main:app
    2. app:app
    3. mini_app:app
    """
    ensure_project_on_path()

    candidates: list[tuple[str, str]] = [
        ("app.main", "app"),
        ("app", "app"),
        ("mini_app", "app"),
    ]

    last_exc: Exception | None = None

    for module_name, attr_name in candidates:
        try:
            module = importlib.import_module(module_name)
            app_obj = getattr(module, attr_name)
            if isinstance(app_obj, FastAPI):
                return app_obj
        except Exception as exc:  # noqa: BLE001
            last_exc = exc

    raise RuntimeError(
        "FastAPI app not found. "
        f"Tried modules: {[m for m, _ in candidates]}. Last error: {last_exc!r}"
    )


def main() -> None:
    app = load_app()
    schema: dict[str, Any] = app.openapi()

    OPENAPI_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPENAPI_PATH.write_text(
        json.dumps(schema, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[generate_openapi] Wrote OpenAPI schema to {OPENAPI_PATH}")


if __name__ == "__main__":
    main()
