from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


# ===========================
# Tabella AZIENDA (tenant)
# ===========================


class Azienda(Base):
    __tablename__ = "azienda"

    id: int = Column(Integer, primary_key=True, index=True)
    nome: str = Column(String(255), nullable=False)
    partita_iva: str | None = Column(String(32), nullable=True)
    slug: str | None = Column(String(64), nullable=True, unique=True)
    codice: str | None = Column(String(64), nullable=True, unique=True)
    indirizzo: str | None = Column(Text, nullable=True)
    note: str | None = Column(Text, nullable=True)

    # Relazioni
    utenti = relationship(
        "Utente", back_populates="azienda", cascade="all, delete-orphan"
    )
    operatori = relationship(
        "Operatore", back_populates="azienda", cascade="all, delete-orphan"
    )
    dpi_items = relationship(
        "DPI", back_populates="azienda", cascade="all, delete-orphan"
    )
    impianti = relationship(
        "ImpiantoAnticaduta",
        back_populates="azienda",
        cascade="all, delete-orphan",
    )
    ispezioni = relationship(
        "Ispezione", back_populates="azienda", cascade="all, delete-orphan"
    )
    corsi = relationship(
        "Corso", back_populates="azienda", cascade="all, delete-orphan"
    )
    attestati = relationship(
        "Attestato", back_populates="azienda", cascade="all, delete-orphan"
    )
    allegati = relationship(
        "Allegato", back_populates="azienda", cascade="all, delete-orphan"
    )


Index("ix_azienda_codice", Azienda.codice)
Index("ix_azienda_slug", Azienda.slug)


# ===========================
# Tabella UTENTE (auth/ruoli)
# ===========================


class Utente(Base):
    __tablename__ = "utente"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email: str = Column(String(255), nullable=False, unique=True, index=True)
    password_hash: str = Column(String(255), nullable=False)
    ruolo: str = Column(String(50), nullable=False)  # es. ADMIN, HSE, DATORE, OPERATORE
    attivo: bool = Column(Boolean, nullable=False, default=True)

    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    azienda = relationship("Azienda", back_populates="utenti")


Index("ix_utente_azienda_id", Utente.azienda_id)


# ===========================
# Tabella OPERATORE
# ===========================


class Operatore(Base):
    __tablename__ = "operatore"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nome: str = Column(String(100), nullable=False)
    cognome: str = Column(String(100), nullable=False)
    utente_id: int | None = Column(
        Integer,
        ForeignKey("utente.id", ondelete="SET NULL"),
        nullable=True,
    )
    attivo: bool = Column(Boolean, nullable=False, default=True)

    azienda = relationship("Azienda", back_populates="operatori")
    utente = relationship("Utente")

    dpi_assegnati = relationship("DPI", back_populates="operatore")
    attestati = relationship("Attestato", back_populates="operatore")


Index("ix_operatore_azienda_id", Operatore.azienda_id)


# ===========================
# Tabella DPI
# ===========================


class DPI(Base):
    __tablename__ = "dpi"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    codice: str = Column(String(100), nullable=False, index=True)
    descrizione: str = Column(String(255), nullable=False)
    categoria: str | None = Column(String(100), nullable=True)
    stato: str = Column(
        String(30), nullable=False, default="OK"
    )  # OK / WARNING / SCADUTO / FUORI_SERVIZIO
    data_scadenza: date | None = Column(Date, nullable=True)

    operatore_id: int | None = Column(
        Integer,
        ForeignKey("operatore.id", ondelete="SET NULL"),
        nullable=True,
    )

    azienda = relationship("Azienda", back_populates="dpi_items")
    operatore = relationship("Operatore", back_populates="dpi_assegnati")
    ispezioni = relationship("Ispezione", back_populates="dpi")


Index("ix_dpi_azienda_id", DPI.azienda_id)
Index("ix_dpi_codice", DPI.codice)
Index("ix_dpi_data_scadenza", DPI.data_scadenza)


# ===========================
# Tabella IMPIANTO ANTICADUTA
# ===========================


class ImpiantoAnticaduta(Base):
    __tablename__ = "impianto_anticaduta"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    codice: str = Column(String(100), nullable=False, index=True)
    descrizione: str = Column(String(255), nullable=False)
    ubicazione: str | None = Column(String(255), nullable=True)
    stato: str = Column(String(30), nullable=False, default="OK")
    data_scadenza: date | None = Column(Date, nullable=True)

    azienda = relationship("Azienda", back_populates="impianti")
    ispezioni = relationship("Ispezione", back_populates="impianto")


Index("ix_impianto_azienda_id", ImpiantoAnticaduta.azienda_id)
Index("ix_impianto_codice", ImpiantoAnticaduta.codice)
Index("ix_impianto_data_scadenza", ImpiantoAnticaduta.data_scadenza)


# ===========================
# Tabella ISPEZIONE
# ===========================


class Ispezione(Base):
    __tablename__ = "ispezione"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tipo_target: str = Column(String(20), nullable=False)  # 'DPI' | 'IMPIANTO'
    dpi_id: int | None = Column(
        Integer,
        ForeignKey("dpi.id", ondelete="CASCADE"),
        nullable=True,
    )
    impianto_id: int | None = Column(
        Integer,
        ForeignKey("impianto_anticaduta.id", ondelete="CASCADE"),
        nullable=True,
    )

    data_ispezione: date = Column(Date, nullable=False)
    esito: str = Column(String(30), nullable=False, default="OK")
    note: str | None = Column(Text, nullable=True)

    operatore_id: int | None = Column(
        Integer,
        ForeignKey("operatore.id", ondelete="SET NULL"),
        nullable=True,
    )

    azienda = relationship("Azienda", back_populates="ispezioni")
    dpi = relationship("DPI", back_populates="ispezioni")
    impianto = relationship("ImpiantoAnticaduta", back_populates="ispezioni")
    allegati = relationship(
        "Allegato", back_populates="ispezione", cascade="all, delete-orphan"
    )
    operatore = relationship("Operatore")


Index("ix_ispezione_azienda_id", Ispezione.azienda_id)
Index("ix_ispezione_data", Ispezione.data_ispezione)


# ===========================
# Tabella ALLEGATO
# ===========================


class Allegato(Base):
    __tablename__ = "allegato"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ispezione_id: int = Column(
        Integer,
        ForeignKey("ispezione.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tipo: str = Column(String(30), nullable=False)  # FOTO / PDF / VIDEO / ALTRO
    file_path: str = Column(String(512), nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    azienda = relationship("Azienda", back_populates="allegati")
    ispezione = relationship("Ispezione", back_populates="allegati")


Index("ix_allegato_azienda_id", Allegato.azienda_id)


# ===========================
# Tabella CORSO
# ===========================


class Corso(Base):
    __tablename__ = "corso"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    titolo: str = Column(String(255), nullable=False)
    descrizione: str | None = Column(Text, nullable=True)
    durata_ore: int | None = Column(Integer, nullable=True)

    azienda = relationship("Azienda", back_populates="corsi")
    attestati = relationship("Attestato", back_populates="corso")


Index("ix_corso_azienda_id", Corso.azienda_id)


# ===========================
# Tabella ATTESTATO
# ===========================


class Attestato(Base):
    __tablename__ = "attestato"

    id: int = Column(Integer, primary_key=True, index=True)
    azienda_id: int = Column(
        Integer,
        ForeignKey("azienda.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    corso_id: int = Column(
        Integer,
        ForeignKey("corso.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operatore_id: int = Column(
        Integer,
        ForeignKey("operatore.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    data_rilascio: date = Column(Date, nullable=False)
    data_scadenza: date | None = Column(Date, nullable=True)
    file_path: str | None = Column(String(512), nullable=True)

    azienda = relationship("Azienda", back_populates="attestati")
    corso = relationship("Corso", back_populates="attestati")
    operatore = relationship("Operatore", back_populates="attestati")


Index("ix_attestato_azienda_id", Attestato.azienda_id)
Index("ix_attestato_data_scadenza", Attestato.data_scadenza)
