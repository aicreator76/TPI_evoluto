import os
import pandas as pd


def load_dpi_excel(excel_path: str, config: dict):
    """
    Lettore "intelligente" per:
    - scadenzario DPI con intestazioni in mezzo al foglio
    - oppure Excel normale con intestazioni in riga 1

    Risultato: DataFrame con nomi colonna normalizzati (minuscolo, underscore).
    """

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"File Excel DPI non trovato: {excel_path}")

    # Leggo TUTTO senza header, così vedo anche le righe di intestazione "strane"
    raw = pd.read_excel(excel_path, header=None)

    header_row_idx = None

    # Cerco una riga che contenga la parola "scadenza"
    # (tipico della tua colonna "Scadenza" nel report DPI)
    for r in range(len(raw)):
        row = raw.iloc[r]
        for val in row:
            if isinstance(val, str) and "scadenza" in val.lower():
                header_row_idx = r
                break
        if header_row_idx is not None:
            break

    if header_row_idx is None:
        # fallback: Excel "normale" con header in prima riga
        df = pd.read_excel(excel_path)
    else:
        # uso quella riga come intestazione e le sotto come dati
        header = raw.iloc[header_row_idx]
        df = raw.iloc[header_row_idx + 1 :].copy()
        df.columns = header

    # reset indici e tolgo righe completamente vuote
    df = df.reset_index(drop=True)
    df = df.dropna(how="all")

    # normalizzo i nomi colonna
    new_cols = []
    for c in df.columns:
        if isinstance(c, str):
            new_cols.append(c.strip().lower().replace(" ", "_"))
        else:
            new_cols.append(str(c))
    df.columns = new_cols

    return df
