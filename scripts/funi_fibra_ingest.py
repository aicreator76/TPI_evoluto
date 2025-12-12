from __future__ import annotations

from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------
# PATH BASE
# --------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_FILE = (
    BASE_DIR
    / "data"
    / "cataloghi"
    / "funi_fibra"
    / "source"
    / "tpi_funi_fibra_famiglie_FOREST+IND.csv"
)

MASTER_DIR = BASE_DIR / "data" / "cataloghi" / "funi_fibra" / "master"
MASTER_CSV = MASTER_DIR / "funi_fibra_master.csv"
MASTER_JSON = MASTER_DIR / "funi_fibra_items.json"


# --------------------------------------------------------------------
# NORMALIZZAZIONE TESTO (fix mojibake tipo â€“, â€ ecc.)
# --------------------------------------------------------------------
REPLACEMENTS = {
    "â€“": "–",  # en dash
    "â€”": "—",  # em dash
    "â€‹": "",  # zero-width
    "â€": "-",  # dash
    "â€‘": "-",  # non-breaking hyphen
    "â€˜": "’",  # apostrofo sinistro
    "â€™": "’",  # apostrofo destro
    "â€œ": "“",  # virgolette aperte
    "â€": "”",  # virgolette chiuse
    "â€": '"',  # fallback generico
    "Â ": "",  # spazio con Â
    "Â°": "°",
    "Ã ": "à",
    "Ã¨": "è",
    "Ã©": "é",
    "Ã¬": "ì",
    "Ã²": "ò",
    "Ã¹": "ù",
    "Ã€": "À",
    "Ã‰": "É",
    "Ã™": "Ù",
    "Ã“": "Ó",
    "Ã†": "Æ",
    "Ã§": "ç",
}


def normalize_text(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None

    text = str(value)
    for bad, good in REPLACEMENTS.items():
        if bad in text:
            text = text.replace(bad, good)
    return text


# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------
def main() -> int:
    print(f"Leggo {SOURCE_FILE} ...")

    if not SOURCE_FILE.exists():
        print(f"[ERRORE] File sorgente non trovato: {SOURCE_FILE}")
        return 1

    MASTER_DIR.mkdir(parents=True, exist_ok=True)

    # Leggiamo forzando UTF-8, ma comunque ripuliamo il testo dopo
    df = pd.read_csv(SOURCE_FILE, dtype=str, encoding="utf-8", keep_default_na=False)

    print(f"Totale righe input : {len(df)}")

    # Deduplica grezza
    df = df.drop_duplicates()
    print(f"Dopo deduplica     : {len(df)}")

    # Normalizziamo le colonne di testo principali
    text_cols = [
        "descrizione",
        "famiglia",
        "macro_famiglia",
        "settore",
        "note",
        "fonte",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].map(normalize_text)

    # Garantiamo la colonna 'scadenza'
    if "scadenza" not in df.columns:
        df["scadenza"] = None

    # Salvataggio CSV + JSON (UTF-8 pulito)
    df.to_csv(MASTER_CSV, index=False, encoding="utf-8")
    df.to_json(MASTER_JSON, orient="records", force_ascii=False, indent=2)

    # Riepilogo macro_famiglia
    if "macro_famiglia" in df.columns:
        print("\nRiepilogo per macro_famiglia:")
        print(df["macro_famiglia"].value_counts())
    else:
        print("\n[WARN] Colonna 'macro_famiglia' non trovata.")

    # Esempio prime righe
    print("\nEsempio prime 5 righe:")
    with pd.option_context("display.max_colwidth", 120):
        print(df.head())

    print(f"\nCSV scritto in: {MASTER_CSV}")
    print(f"JSON scritto in: {MASTER_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
