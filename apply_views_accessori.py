import sqlite3
from pathlib import Path

DB_PATH = Path(r"E:\CLONAZIONE\tpi_evoluto\tpi.db")
SQL_PATH = Path(r"E:\CLONAZIONE\tpi_evoluto\sql\create_views_accessori_3_0_2025-12-08.sql")

if not DB_PATH.exists():
    raise SystemExit(f"DB non trovato: {DB_PATH}")

if not SQL_PATH.exists():
    raise SystemExit(f"File SQL non trovato: {SQL_PATH}")

print(f"[INFO] Applico VIEW da {SQL_PATH} su {DB_PATH}...")
con = sqlite3.connect(DB_PATH)
try:
    sql = SQL_PATH.read_text(encoding="utf-8")
    con.executescript(sql)
    con.commit()
    print("[OK] VIEW create/aggiornate.")
finally:
    con.close()
