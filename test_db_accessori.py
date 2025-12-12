import sqlite3
from pathlib import Path

db = Path(r"E:\CLONAZIONE\tpi_evoluto\tpi.db")
print("DB esiste:", db.exists(), "→", db)

if not db.exists():
    print("ATTENZIONE: DB non trovato, fermo il test.")
    raise SystemExit(1)

con = sqlite3.connect(db)
cur = con.cursor()

tabelle = [
    "tpi_accessori_famiglie",
    "tpi_accessori_morsetti",
    "tpi_accessori_catena_g8",
    "tpi_accessori_tycan",
]

for t in tabelle:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        print(f"{t:28s} → {n} righe")
    except Exception as e:
        print(f"{t:28s} → ERRORE:", e)

con.close()
