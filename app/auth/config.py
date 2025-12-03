"""
Config base per autenticazione JWT TPI_evoluto.

Per l'ambiente reale, sovrascrivi le variabili di ambiente:

- TPI_SECRET_KEY
- TPI_ACCESS_TOKEN_EXPIRE_MINUTES
"""

from __future__ import annotations

import os


# Chiave di firma JWT (DEV: va cambiata in produzione!)
SECRET_KEY: str = os.getenv("TPI_SECRET_KEY", "DEV-CHANGE-ME-SECRET")

# Algoritmo di firma
ALGORITHM: str = "HS256"

# Scadenza token in minuti (default: 60)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("TPI_ACCESS_TOKEN_EXPIRE_MINUTES", "60"),
)
