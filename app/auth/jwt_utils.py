from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import ExpiredSignatureError, PyJWTError

# -------------------------------------------------------------------
# Compat: in precedenza deps.py si aspettava InvalidTokenError.
# Ora la reintroduciamo per non toccare deps.py.
# -------------------------------------------------------------------


class InvalidTokenError(Exception):
    """Token JWT non valido o scaduto."""


# -------------------------------------------------------------------
# Config (env-first). Mantieni compatibilità senza toccare altri file.
# -------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", ""))
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")  # opzionale
JWT_ISSUER = os.getenv("JWT_ISSUER")  # opzionale


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Crea JWT (access token).
    - Aggiunge exp
    - Usa SECRET_KEY + ALGORITHM
    """
    if not SECRET_KEY:
        raise RuntimeError("Missing JWT secret key (set JWT_SECRET_KEY or SECRET_KEY)")

    to_encode = dict(data)
    expire = _utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire

    if JWT_AUDIENCE:
        to_encode.setdefault("aud", JWT_AUDIENCE)
    if JWT_ISSUER:
        to_encode.setdefault("iss", JWT_ISSUER)

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodifica e valida JWT.
    - Verifica firma
    - Verifica exp
    - Se AUD/ISS sono settati in env, li valida.
    Ritorna payload dict oppure alza InvalidTokenError (compat).
    """
    if not SECRET_KEY:
        raise RuntimeError("Missing JWT secret key (set JWT_SECRET_KEY or SECRET_KEY)")

    try:
        kwargs: dict[str, Any] = {}
        if JWT_AUDIENCE:
            kwargs["audience"] = JWT_AUDIENCE
        if JWT_ISSUER:
            kwargs["issuer"] = JWT_ISSUER

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], **kwargs)

        if not isinstance(payload, dict):
            raise InvalidTokenError("Invalid token payload")

        return payload

    except ExpiredSignatureError as exc:
        raise InvalidTokenError("Token expired") from exc
    except PyJWTError as exc:
        raise InvalidTokenError("Invalid token") from exc
