"""
Package auth TPI_evoluto: JWT, ruoli e dipendenze FastAPI.
"""

from __future__ import annotations

from app.auth import config, deps, jwt_utils, router, schemas

__all__ = ["config", "deps", "jwt_utils", "router", "schemas"]
