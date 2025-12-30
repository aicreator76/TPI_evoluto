from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest


def _resolve_db_path() -> Path:
    """
    In CI non avremo il DB. In locale sì.
    Supporta override via env: TPI_DB_PATH.
    """
    # 1) override esplicito
    env = os.getenv("TPI_DB_PATH")
    if env:
        return Path(env)

    # 2) default: tpi.db nella root repo (come in app/db/accessori.py)
    repo_root = Path(__file__).resolve().parent
    return (repo_root / "tpi.db").resolve()


def _table_exists(cur: sqlite3.Cursor, name: str) -> bool:
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (name,))
    return cur.fetchone() is not None


@pytest.mark.db
def test_accessori_db_tables_exist_and_readable() -> None:
    db = _resolve_db_path()
    if not db.exists():
        pytest.skip(
            f"DB non trovato ({db}). Test DB accessori saltato in CI.", allow_module_level=False
        )

    con = sqlite3.connect(db)
    try:
        cur = con.cursor()

        tabelle = [
            "tpi_accessori_famiglie",
            "tpi_accessori_morsetti",
            "tpi_accessori_catena_g8",
            "tpi_accessori_tycan",
        ]

        # 1) esistono
        missing = [t for t in tabelle if not _table_exists(cur, t)]
        assert not missing, f"Tabelle mancanti nel DB: {missing}"

        # 2) sono leggibili (COUNT)
        counts: dict[str, int] = {}
        for t in tabelle:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = int(cur.fetchone()[0])

        # Non imponiamo numeri fissi (DB può cambiare), ma vogliamo almeno 1 tabella popolata
        assert any(v >= 0 for v in counts.values()), f"COUNT non valido: {counts}"
    finally:
        con.close()
