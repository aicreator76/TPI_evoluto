from __future__ import annotations
import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MASTER_CSV = BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "master" / "funi_fibra_master.csv"

FORESTALE_DIR = BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "forestale"
INDUSTRIALE_DIR = BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "industriale"
SOLLEVAMENTO_DIR = BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "sollevamento"

for d in (FORESTALE_DIR, INDUSTRIALE_DIR, SOLLEVAMENTO_DIR):
    d.mkdir(parents=True, exist_ok=True)


def cluster(row: pd.Series) -> str:
    """Decide in quale 'care' mandare la famiglia."""
    settore = str(row.get("settore", "")).lower()

    if "forestale" in settore:
        return "forestale"
    if "sollevamento" in settore:
        return "sollevamento"
    # fallback: tutto il resto va in industriale
    return "industriale"


def salva(df: pd.DataFrame, directory: Path, nome_base: str) -> None:
    csv_path = directory / f"{nome_base}.csv"
    json_path = directory / f"{nome_base}.json"

    df.to_csv(csv_path, index=False, encoding="utf-8")
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

    print(f"- {len(df):3d} righe → {csv_path.name} / {json_path.name} in {directory}")


def main() -> None:
    if not MASTER_CSV.exists():
        raise SystemExit(f"Master CSV non trovato: {MASTER_CSV}")

    print(f"Leggo master: {MASTER_CSV}")
    df = pd.read_csv(MASTER_CSV)

    df["care"] = df.apply(cluster, axis=1)

    df_forestale = df[df["care"] == "forestale"].drop(columns=["care"])
    df_sollevamento = df[df["care"] == "sollevamento"].drop(columns=["care"])
    df_industriale = df[df["care"] == "industriale"].drop(columns=["care"])

    print(f"Totale master: {len(df)} righe")
    print(
        "Distribuzione care:",
        df["care"].value_counts(dropna=False).to_dict(),
        sep="\n",
    )

    print("\nScrivo file per ciascuna care...")
    salva(df_forestale, FORESTALE_DIR, "funi_fibra_forestale")
    salva(df_sollevamento, SOLLEVAMENTO_DIR, "funi_fibra_sollevamento")
    salva(df_industriale, INDUSTRIALE_DIR, "funi_fibra_industriale")

    print("\nDONE.")


if __name__ == "__main__":
    main()
