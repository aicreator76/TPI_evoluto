"""
Router /auth per ottenere un JWT di sviluppo.

IMPORTANTE:
- Questa versione NON verifica la password su DB.
- Usa il solo username (email) e assegna ruolo OPERATORE e azienda_id=1.
- Serve come base tecnica per issue #50, in attesa di aggancio al DB utenti.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.jwt_utils import create_access_token
from app.auth.schemas import Role, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Endpoint DEV per ottenere un token JWT.

    - Accetta qualsiasi combinazione username/password.
    - Usa username come email nel claim `sub`.
    - Imposta ruolo di default OPERATORE e azienda_id=1.
    """

    # In futuro: qui andrà la verifica contro tabella `utente` (email + password_hash)
    access_token = create_access_token(
        {
            "sub": form_data.username,
            "role": Role.OPERATORE.value,
            "azienda_id": 1,
        },
    )

    return Token(access_token=access_token, token_type="bearer")
