from pathlib import Path
import pandas as pd


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]

    # SORGENTE: catalogo master (DPI + FORESTALE + altro)
    src_csv = base_dir / "data" / "cataloghi" / "imports" / "catalogo_20251205_011611.csv"

    if not src_csv.exists():
        raise SystemExit(f"Sorgente non trovata: {src_csv}")

    df = pd.read_csv(src_csv)
    df.columns = [c.strip().lower() for c in df.columns]

    # Colonne minime che ci servono
    for col in ("codice", "descrizione", "gruppo"):
        if col not in df.columns:
            df[col] = ""

    # FILTRO: solo articoli forestali (funi + accessori forestali)
    mask_forest = df["codice"].astype(str).str.startswith("TPI-FOREST-")
    df_forest = df.loc[mask_forest].copy()

    if df_forest.empty:
        raise SystemExit("Nessun codice TPI-FOREST- trovato nel catalogo master.")

    # Metadati TPI per CARE funi_fibra (forestale)
    df_forest["segmento"] = "FORESTALE"  # dove lavora: bosco / verricelli / gru a cavo
    df_forest["macro_famiglia"] = "FUNE_FIBRA"  # bucket commerciale principale
    df_forest["attivo"] = 1  # 1 = visibile/usabile in app

    # Ordine colonne v0.1
    cols = [
        "codice",
        "descrizione",
        "gruppo",
        "segmento",
        "macro_famiglia",
        "attivo",
    ]
    df_out = df_forest[cols]

    out_csv = base_dir / "docs" / "catalogo" / "funi_fibra_forestale.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_csv, index=False, encoding="utf-8")

    print(f"[funi_fibra_forestale] Salvati {len(df_out)} record in {out_csv}")


if __name__ == "__main__":
    main()
