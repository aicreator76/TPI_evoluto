from pathlib import Path
import sqlite3

DB_PATH = Path("tpi.db")
SQL_PATH = Path("sql/apply_views_lynx_dpi_2025-12-12.sql")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit(f"DB mancante: {DB_PATH.resolve()}")
    if not SQL_PATH.exists():
        raise SystemExit(f"SQL mancante: {SQL_PATH.resolve()}")

    sql = SQL_PATH.read_text(encoding="utf-8", errors="ignore")
    with sqlite3.connect(DB_PATH) as con:
        con.executescript(sql)
    print("OK: viste LYNX DPI applicate")


if __name__ == "__main__":
    main()
