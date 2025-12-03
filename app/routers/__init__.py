"""
Package dei router applicativi TPI_evoluto.

Uso:
    from app.routers import csv_import, csv_export_filtered, ops, nfc_routes
"""

from . import csv_import, csv_export_filtered, ops, nfc_routes

__all__ = [
    "csv_import",
    "csv_export_filtered",
    "ops",
    "nfc_routes",
]
