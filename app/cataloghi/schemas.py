import re
from pydantic import BaseModel, Field, HttpUrl, field_validator

CODICE_RE = re.compile(r"^[A-Z0-9\-_]{3,32}$")


class CatalogoBase(BaseModel):
    codice: str = Field(..., min_length=3, max_length=32)
    descrizione: str | None = None
    categoria: str | None = None
    prezzo_eur: float | None = Field(default=None, ge=0)
    url: HttpUrl | None = None

    @field_validator("codice")
    @classmethod
    def _codice_ok(cls, v: str) -> str:
        if not CODICE_RE.match(v):
            raise ValueError("codice non valido [A-Z0-9-_]{3,32}")
        return v


class DpiRow(CatalogoBase):
    pass


class AncoraggioRow(CatalogoBase):
    pass
