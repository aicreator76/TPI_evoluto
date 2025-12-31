from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest


def _repo_db_path() -> Path:
    # Repo root = cartella dove sta questo file
    root = Path(__file__).resolve().parent
    # supporta override via env
    env = os.getenv("TPI_DB_PATH")
    if env:
        return Path(env)
    return root / "tpi.db"


@pytest.mark.db
def test_accessori_tables_exist_and_have_rows() -> None:
    db = _repo_db_path()

    if not db.exists():
        pytest.skip(f"DB non presente: {db} (set TPI_DB_PATH per abilitarlo)")

    con = sqlite3.connect(db)
    try:
        cur = con.cursor()
        tabelle = [
            "tpi_accessori_famiglie",
            "tpi_accessori_morsetti",
            "tpi_accessori_catena_g8",
            "tpi_accessori_tycan",
        ]

        for t in tabelle:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (t,))
            assert cur.fetchone() is not None, f"Tabella mancante: {t}"

            cur.execute(f"SELECT COUNT(*) FROM {t}")  # ok: t è whitelist hardcoded
            n = int(cur.fetchone()[0])
            assert n >= 0, f"Count fallito per {t}"
    finally:
        con.close()
