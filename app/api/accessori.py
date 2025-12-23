from __future__ import annotations

# Compat shim: vecchio import "app.api.accessori" -> router reale
from app.api.accessori_listino import router  # noqa: F401
