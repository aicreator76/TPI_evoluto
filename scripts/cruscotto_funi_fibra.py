from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
MASTER = BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "master" / "funi_fibra_master.csv"
FORESTALE = (
    BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "forestale" / "funi_fibra_forestale.csv"
)
SOLLEVAMENTO = (
    BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "sollevamento" / "funi_fibra_sollevamento.csv"
)
INDUSTRIALE = (
    BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "industriale" / "funi_fibra_industriale.csv"
)


def _load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    # per ora lasciamo l'encoding così; lo aggiusteremo a monte nell’ingest
    return pd.read_csv(path)


def main() -> None:
    now = dt.datetime.now().isoformat(timespec="seconds")

    df_master = _load_csv(MASTER)
    df_forest = _load_csv(FORESTALE)
    df_soll = _load_csv(SOLLEVAMENTO)
    df_ind = _load_csv(INDUSTRIALE)

    tot = len(df_master)
    n_forest = len(df_forest)
    n_soll = len(df_soll)
    n_ind = len(df_ind)

    # scadenze valorizzate (per futuro): ora saranno 0
    has_scadenza = df_master["scadenza"].notna().sum() if "scadenza" in df_master.columns else 0

    print("Cruscotto FUNI IN FIBRA")
    print("=" * 40)
    print(f"Ultimo aggiornamento: {now}")
    print()
    print(f"Totale famiglie in master : {tot}")
    print(f"  - Forestale             : {n_forest}")
    print(f"  - Sollevamento          : {n_soll}")
    print(f"  - Industriale           : {n_ind}")
    print()
    print(f"Record con campo scadenza valorizzato: {has_scadenza}")
    print()
    print("File sorgente:")
    print(f"  master      → {MASTER}")
    print(f"  forestale   → {FORESTALE}")
    print(f"  sollevamento→ {SOLLEVAMENTO}")
    print(f"  industriale → {INDUSTRIALE}")


if __name__ == "__main__":
    main()
