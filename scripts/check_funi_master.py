from pathlib import Path

import pandas as pd


def main() -> None:
    path = Path(r"E:\CLONAZIONE\tpi_evoluto\data\cataloghi\funi_fibra\master\funi_fibra_master.csv")
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    print("=== HEAD FUNI_FIBRA MASTER (prime 5 righe) ===")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
