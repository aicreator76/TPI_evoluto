"""init schema TPI v1

Revision: 14252af2016e
This migration creates the initial schema for TPI_evoluto (azienda, utenti, operatori,
dpi, impianti_anticaduta, ispezioni, allegati, corsi, attestati).
"""

from alembic import op  # type: ignore[attr-defined]
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "14252af2016e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types for Postgres (safe to execute only on Postgres)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE TYPE ruolo_enum AS ENUM ('admin', 'operatore', 'superadmin')")
        op.execute(
            "CREATE TYPE stato_dpi_enum AS ENUM ('disponibile', 'assegnato', 'ritirato', 'scaduto')"
        )
        op.execute(
            "CREATE TYPE esito_ispezione_enum AS ENUM ('positivo', 'negativo', 'da_rivedere')"
        )
        op.execute("CREATE TYPE tipo_target_enum AS ENUM ('DPI', 'IMPIANTO')")

    # azienda
    op.create_table(
        "azienda",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(length=128), nullable=False),
        sa.Column("partita_iva", sa.String(length=20), nullable=True, unique=True),
        sa.Column("config_json", sa.Text(), nullable=True),
    )

    # utente
    op.create_table(
        "utente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True),
        sa.Column("email", sa.String(length=128), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=256), nullable=False),
        sa.Column(
            "ruolo",
            sa.Enum(
                "admin",
                "operatore",
                "superadmin",
                name="ruolo_enum",
                create_type=False,  # IMPORTANT: type already created above on Postgres
            ),
            nullable=False,
        ),
    )
    op.create_index("ix_utente_azienda_id", "utente", ["azienda_id"])

    # operatore
    op.create_table(
        "operatore",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=64), nullable=True),
        sa.Column("cognome", sa.String(length=64), nullable=True),
        sa.Column("codice_fiscale", sa.String(length=16), nullable=True, unique=True),
    )
    op.create_index("ix_operatore_azienda_id", "operatore", ["azienda_id"])

    # dpi
    op.create_table(
        "dpi",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=128), nullable=True),
        sa.Column("tipo", sa.String(length=64), nullable=True),
        sa.Column("codice", sa.String(length=64), nullable=True, unique=True),
        sa.Column("data_scadenza", sa.Date(), nullable=True),
        sa.Column(
            "stato",
            sa.Enum(
                "disponibile",
                "assegnato",
                "ritirato",
                "scaduto",
                name="stato_dpi_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "operatore_id",
            sa.Integer(),
            sa.ForeignKey("operatore.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("note", sa.Text(), nullable=True),
    )
    op.create_index("ix_dpi_azienda_id", "dpi", ["azienda_id"])
    op.create_index("ix_dpi_codice", "dpi", ["codice"])
    op.create_index("ix_dpi_data_scadenza", "dpi", ["data_scadenza"])

    # impianto_anticaduta
    op.create_table(
        "impianto_anticaduta",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=128), nullable=True),
        sa.Column("tipo", sa.String(length=64), nullable=True),
        sa.Column("codice", sa.String(length=64), nullable=True, unique=True),
        sa.Column("data_installazione", sa.Date(), nullable=True),
        sa.Column("stato", sa.String(length=64), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
    )
    op.create_index("ix_impianto_azienda_id", "impianto_anticaduta", ["azienda_id"])
    op.create_index("ix_impianto_codice", "impianto_anticaduta", ["codice"])

    # ispezione
    op.create_table(
        "ispezione",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "dpi_id",
            sa.Integer(),
            sa.ForeignKey("dpi.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "impianto_id",
            sa.Integer(),
            sa.ForeignKey("impianto_anticaduta.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "operatore_id",
            sa.Integer(),
            sa.ForeignKey("operatore.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column(
            "esito",
            sa.Enum(
                "positivo",
                "negativo",
                "da_rivedere",
                name="esito_ispezione_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "tipo_target",
            sa.Enum("DPI", "IMPIANTO", name="tipo_target_enum", create_type=False),
            nullable=False,
        ),
    )
    op.create_index("ix_ispezione_azienda_id", "ispezione", ["azienda_id"])
    op.create_index("ix_ispezione_data", "ispezione", ["data"])
    op.create_index("ix_ispezione_dpi_id", "ispezione", ["dpi_id"])
    op.create_index("ix_ispezione_impianto_id", "ispezione", ["impianto_id"])

    # allegato
    op.create_table(
        "allegato",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "ispezione_id",
            sa.Integer(),
            sa.ForeignKey("ispezione.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "dpi_id",
            sa.Integer(),
            sa.ForeignKey("dpi.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "impianto_id",
            sa.Integer(),
            sa.ForeignKey("impianto_anticaduta.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("percorso_file", sa.String(length=512), nullable=False),
        sa.Column("tipo", sa.String(length=64), nullable=True),
        sa.Column("creato_il", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_allegato_azienda_id", "allegato", ["azienda_id"])
    op.create_index("ix_allegato_ispezione_id", "allegato", ["ispezione_id"])

    # corso
    op.create_table(
        "corso",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "operatore_id",
            sa.Integer(),
            sa.ForeignKey("operatore.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nome", sa.String(length=128), nullable=True),
        sa.Column("data_inizio", sa.Date(), nullable=True),
        sa.Column("data_fine", sa.Date(), nullable=True),
    )
    op.create_index("ix_corso_azienda_id", "corso", ["azienda_id"])

    # attestato
    op.create_table(
        "attestato",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "azienda_id",
            sa.Integer(),
            sa.ForeignKey("azienda.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "corso_id",
            sa.Integer(),
            sa.ForeignKey("corso.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "operatore_id",
            sa.Integer(),
            sa.ForeignKey("operatore.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("data_rilascio", sa.Date(), nullable=True),
        sa.Column("descrizione", sa.Text(), nullable=True),
    )
    op.create_index("ix_attestato_azienda_id", "attestato", ["azienda_id"])
    op.create_index("ix_attestato_data_rilascio", "attestato", ["data_rilascio"])


def downgrade() -> None:
    bind = op.get_bind()

    # Drop tables in reverse order to avoid FK conflicts
    op.drop_index("ix_attestato_data_rilascio", table_name="attestato")
    op.drop_index("ix_attestato_azienda_id", table_name="attestato")
    op.drop_table("attestato")

    op.drop_index("ix_corso_azienda_id", table_name="corso")
    op.drop_table("corso")

    op.drop_index("ix_allegato_ispezione_id", table_name="allegato")
    op.drop_index("ix_allegato_azienda_id", table_name="allegato")
    op.drop_table("allegato")

    op.drop_index("ix_ispezione_impianto_id", table_name="ispezione")
    op.drop_index("ix_ispezione_dpi_id", table_name="ispezione")
    op.drop_index("ix_ispezione_data", table_name="ispezione")
    op.drop_index("ix_ispezione_azienda_id", table_name="ispezione")
    op.drop_table("ispezione")

    op.drop_index("ix_impianto_codice", table_name="impianto_anticaduta")
    op.drop_index("ix_impianto_azienda_id", table_name="impianto_anticaduta")
    op.drop_table("impianto_anticaduta")

    op.drop_index("ix_dpi_data_scadenza", table_name="dpi")
    op.drop_index("ix_dpi_codice", table_name="dpi")
    op.drop_index("ix_dpi_azienda_id", table_name="dpi")
    op.drop_table("dpi")

    op.drop_index("ix_operatore_azienda_id", table_name="operatore")
    op.drop_table("operatore")

    op.drop_index("ix_utente_azienda_id", table_name="utente")
    op.drop_table("utente")

    op.drop_table("azienda")

    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS tipo_target_enum")
        op.execute("DROP TYPE IF EXISTS esito_ispezione_enum")
        op.execute("DROP TYPE IF EXISTS stato_dpi_enum")
        op.execute("DROP TYPE IF EXISTS ruolo_enum")
