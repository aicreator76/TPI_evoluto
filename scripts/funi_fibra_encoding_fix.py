from __future__ import annotations

from pathlib import Path

import pandas as pd

# ----------------------------------------------------
# PERCORSI COMPLETI (fissi su E:\CLONAZIONE\tpi_evoluto\...)
# ----------------------------------------------------
CSV_PATHS = [
    Path(r"E:\CLONAZIONE\tpi_evoluto\data\cataloghi\funi_fibra\master\funi_fibra_master.csv"),
    Path(r"E:\CLONAZIONE\tpi_evoluto\data\cataloghi\funi_fibra\forestale\funi_fibra_forestale.csv"),
    Path(
        r"E:\CLONAZIONE\tpi_evoluto\data\cataloghi\funi_fibra\sollevamento\funi_fibra_sollevamento.csv"
    ),
    Path(
        r"E:\CLONAZIONE\tpi_evoluto\data\cataloghi\funi_fibra\industriale\funi_fibra_industriale.csv"
    ),
]


# ----------------------------------------------------
# MAPPA MOJIBAKE → CARATTERI GIUSTI
# (UTF-8 italiano tipico)
# ----------------------------------------------------
REPLACEMENTS = {
    # trattini / punteggiatura
    "â€“": "–",
    "â€”": "—",
    "â€¦": "…",
    # virgolette
    "â€œ": "“",
    "â€": "”",
    "â€˜": "‘",
    "â€™": "’",
    # spazi/lettere strane
    "Â®": "®",
    "Â°": "°",
    "Â²": "²",
    "Â³": "³",
    "Âµ": "µ",
    # vocali accentate IT (Ã + lettera)
    "Ã ": "à",
    "Ã¡": "á",
    "Ã¨": "è",
    "Ã©": "é",
    "Ã¬": "ì",
    "Ã­": "í",
    "Ã²": "ò",
    "Ã³": "ó",
    "Ã¹": "ù",
    "Ãº": "ú",
    # altre combinazioni frequenti
    "Â ": " ",  # spazio non-break
    "â€š": "‚",
    "â€ž": "„",
}


def _apply_replacements(text: str) -> str:
    """Applica sostituzioni secche REPLACEMENTS."""
    fixed = text
    for bad, good in REPLACEMENTS.items():
        if bad in fixed:
            fixed = fixed.replace(bad, good)
    # pulizia doppi spazi
    while "  " in fixed:
        fixed = fixed.replace("  ", " ")
    return fixed


def fix_mojibake(value: object) -> object:
    """
    Fix robusto per mojibake IT:

    1. Prova latin1→utf8 (se ha senso).
    2. Applica mappa REPLACEMENTS.
    """
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return value

    s = str(value)

    # 1) tentativo latin1→utf8 (best effort, non obbligatorio)
    try:
        candidate = s.encode("latin1").decode("utf-8")
        s = candidate
    except (UnicodeEncodeError, UnicodeDecodeError):
        # se non torna utile, resta com'è
        pass

    # 2) sostituzioni secche
    s = _apply_replacements(s)
    return s


def fix_csv(path: Path) -> None:
    if not path.exists():
        print(f"[SKIP] File non trovato: {path}")
        return

    print(f"[FIX] {path}")
    # Leggiamo tutto come stringa per non perdere niente
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    for col in df.columns:
        df[col] = df[col].map(fix_mojibake)

    # Scriviamo in UTF-8 pulito
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"      → OK ({len(df)} righe)")


def main() -> int:
    print("=== FIX ENCODING FUNI_FIBRA (latin1→utf8 + map) ===")
    for csv_path in CSV_PATHS:
        fix_csv(csv_path)
    print("=== COMPLETATO ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
