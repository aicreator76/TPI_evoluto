from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, func


class Base(DeclarativeBase):
    pass


class Dpi(Base):
    __tablename__ = "catalogo_dpi"
    codice: Mapped[str] = mapped_column(String(32), primary_key=True)
    descrizione: Mapped[str | None] = mapped_column(String(255), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prezzo_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Ancoraggio(Base):
    __tablename__ = "catalogo_ancoraggi"
    codice: Mapped[str] = mapped_column(String(32), primary_key=True)
    descrizione: Mapped[str | None] = mapped_column(String(255), nullable=True)
    categoria: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prezzo_eur: Mapped[float | None] = mapped_column(Float, nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
