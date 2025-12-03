"""
Utility per creare e validare JWT.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from app.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


class InvalidTokenError(Exception):
    """Errore generico quando il token JWT non è valido."""


def create_access_token(
    data: Dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Crea un JWT firmato con SECRET_KEY.

    Il payload deve contenere almeno:
    - sub: email utente
    - role: ruolo applicativo
    - azienda_id: tenant (opzionale)
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodifica il token JWT e ritorna il payload.

    Lancia InvalidTokenError se il token è invalido o scaduto.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise InvalidTokenError("Token JWT non valido o scaduto") from exc

    return payload
