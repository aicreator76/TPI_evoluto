from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict


# ==================================================
#  CRUSCOTTO ACCESSORI 3.0 – TPI
#  Legge SOLO dalle CSV 3.0 in:
#  E:\CLONAZIONE\import\TPI_READY
# ==================================================

CSV_DIR = Path(r"E:\CLONAZIONE\import\TPI_READY")


def _count_rows(csv_path: Path) -> int:
    if not csv_path.exists():
        return 0
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # salta header
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def main() -> None:
    print("Cruscotto ACCESSORI 3.0")
    print("========================================")

    # --- Famiglie (punti ancoraggio / morsetti / tiranti / catene / tycan) ---
    fam_files: Dict[str, Path] = {
        "Punti ancoraggio (famiglie)": CSV_DIR / "accessori_punti_ancoraggio_famiglie_3.0.csv",
        "Morsetti (famiglie)": CSV_DIR / "accessori_morsetti_famiglie_3.0.csv",
        "Tiranti / brache (famiglie)": CSV_DIR / "accessori_tiranti_brache_famiglie_3.0.csv",
        "Catena G8 (famiglie)": CSV_DIR / "accessori_catena_G8_famiglie_3.0.csv",
        "Catene TYCAN (famiglie)": CSV_DIR / "accessori_catene_TYCAN_famiglie_3.0.csv",
        "TUTTE le famiglie (ALL)": CSV_DIR / "accessori_famiglie_3.0_ALL.csv",
    }

    print("\nFAMIGLIE ACCESSORI")
    print("----------------------------------------")
    tot_fam = 0
    for label, path in fam_files.items():
        n = _count_rows(path)
        tot_fam += n
        print(f"- {label:<35} : {n:4d}  ({path.name})")
    print(f"\nTotale famiglie (somma semplice)        : {tot_fam:4d}")

    # --- Codici (morsetti / catena G8 / TYCAN) ---
    cod_files: Dict[str, Path] = {
        "Morsetti (codici)": CSV_DIR / "accessori_morsetti_codici_3.0.csv",
        "Catena G8 (codici)": CSV_DIR / "accessori_catena_G8_codici_3.0.csv",
        "TYCAN (codici)": CSV_DIR / "accessori_tycan_codici_3.0.csv",
    }

    print("\nCODICI ACCESSORI")
    print("----------------------------------------")
    tot_cod = 0
    for label, path in cod_files.items():
        n = _count_rows(path)
        tot_cod += n
        print(f"- {label:<35} : {n:4d}  ({path.name})")
    print(f"\nTotale codici (somma semplice)          : {tot_cod:4d}")

    print("\nSorgente CSV directory:")
    print(f"  → {CSV_DIR}")


if __name__ == "__main__":
    main()
