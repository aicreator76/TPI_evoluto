"""
Schemi Pydantic e ruoli base per autenticazione JWT.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, EmailStr


class Role(str, Enum):
    ADMIN = "ADMIN"
    HSE = "HSE"
    DATORE = "DATORE"
    OPERATORE = "OPERATORE"
    VISUALIZZATORE = "VISUALIZZATORE"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: EmailStr | None = None
    role: Role | None = None
    azienda_id: int | None = None


class CurrentUser(BaseModel):
    """Rappresenta l'utente autenticato ricostruito dal token."""

    email: EmailStr
    role: Role
    azienda_id: int | None = None
