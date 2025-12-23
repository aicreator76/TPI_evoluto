import os
import sys
from logging.config import fileConfig
from alembic import context  # type: ignore[attr-defined]
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------
# Aggiunge la root del progetto a sys.path
# (env.py sta in E:\CLONAZIONE\tpi_evoluto\alembic\env.py)
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ora possiamo importare app.*
from app.db.base import Base  # noqa: E402


# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata target per autogenerate
target_metadata = Base.metadata


def _get_database_url() -> str:
    """Prende la DATABASE_URL da env o da alembic.ini."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Esegui le migrazioni in modalità 'offline'."""
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Esegui le migrazioni in modalità 'online'."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
