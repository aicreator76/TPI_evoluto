"""
Dependencies FastAPI per ottenere l'utente corrente dal token JWT.

Questa versione NON interroga il database:
riconstruisce l'utente esclusivamente dai claim del token.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.jwt_utils import InvalidTokenError, decode_access_token
from app.auth.schemas import CurrentUser, Role, TokenData

# Endpoint usato da OAuth2 per ottenere il token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Estrae l'utente corrente dal token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except InvalidTokenError as exc:  # pragma: no cover - comportamento standard
        raise credentials_exception from exc

    email = payload.get("sub")
    role_raw = payload.get("role")
    azienda_id = payload.get("azienda_id")

    if email is None or role_raw is None:
        raise credentials_exception

    try:
        role = Role(role_raw)
    except ValueError as exc:
        raise credentials_exception from exc

    token_data = TokenData(email=email, role=role, azienda_id=azienda_id)

    if token_data.email is None or token_data.role is None:
        raise credentials_exception

    return CurrentUser(
        email=token_data.email,
        role=token_data.role,
        azienda_id=token_data.azienda_id,
    )


async def require_role(
    current_user: CurrentUser = Depends(get_current_user),
    *,
    allowed_roles: list[Role],
) -> CurrentUser:
    """
    Dependency riusabile per proteggere endpoint in base al ruolo.

    Esempio d'uso in un router:

    @router.get("/segreto")
    async def endpoint(
        user: CurrentUser = Depends(
            lambda: require_role(allowed_roles=[Role.ADMIN, Role.HSE])
        )
    ):
        ...
    """
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permessi insufficienti per accedere a questa risorsa",
        )

    return current_user
