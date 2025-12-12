from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]

dpi_path = BASE_DIR / "data" / "cataloghi" / "clean" / "dpi_items.json"

funi_base = BASE_DIR / "data" / "cataloghi" / "funi_fibra"
forestale_path = funi_base / "forestale" / "forestale_items.json"
industriale_path = funi_base / "industriale" / "industriale_items.json"
sollevamento_path = funi_base / "sollevamento" / "sollevamento_items.json"


def main() -> None:
    with dpi_path.open("r", encoding="utf-8") as f:
        items = json.load(f)

    # 1) prendo tutte le funi forestali (TPI-FOREST-...)
    forestali = [it for it in items if str(it.get("codice", "")).startswith("TPI-FOREST-")]

    # per ora industriale/sollevamento vuoti (li popoleremo più avanti)
    industriali: list[dict] = []
    sollevamento: list[dict] = []

    # 2) resto = veri DPI (senza forestali)
    dpi_puliti = [it for it in items if it not in forestali]

    funi_base.mkdir(parents=True, exist_ok=True)
    forestale_path.parent.mkdir(parents=True, exist_ok=True)
    industriale_path.parent.mkdir(parents=True, exist_ok=True)
    sollevamento_path.parent.mkdir(parents=True, exist_ok=True)

    with forestale_path.open("w", encoding="utf-8") as f:
        json.dump(forestali, f, ensure_ascii=False, indent=2)

    with industriale_path.open("w", encoding="utf-8") as f:
        json.dump(industriali, f, ensure_ascii=False, indent=2)

    with sollevamento_path.open("w", encoding="utf-8") as f:
        json.dump(sollevamento, f, ensure_ascii=False, indent=2)

    with dpi_path.open("w", encoding="utf-8") as f:
        json.dump(dpi_puliti, f, ensure_ascii=False, indent=2)

    print(f"Totale originale: {len(items)}")
    print(f"  → Forestali spostate: {len(forestali)}")
    print(f"  → DPI rimanenti:     {len(dpi_puliti)}")


if __name__ == "__main__":
    main()
