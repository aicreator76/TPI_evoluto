import os
import json
from datetime import datetime

import pandas as pd

ROOT = r"E:\CLONAZIONE\tpi_evoluto"

LOG_DIR = os.path.join(ROOT, "logs")
CRUSCOTTO_JSON = os.path.join(LOG_DIR, "agente0_dashboard.json")
CRUSCOTTO_HTML = os.path.join(LOG_DIR, "agente0_cruscotto.html")

DPI_CSV = os.path.join(ROOT, "data", "dpi.csv")


def carica_dpi_da_csv() -> pd.DataFrame:
    if not os.path.exists(DPI_CSV):
        raise FileNotFoundError(f"File DPI non trovato: {DPI_CSV}")
    df = pd.read_csv(DPI_CSV)
    return df


def calcola_cruscotto(df: pd.DataFrame) -> dict:
    totale = len(df)

    ok = 0
    warning = 0
    scaduti = 0
    anomalie = 0

    oggi = datetime.now().date()

    for _, riga in df.iterrows():
        valore = riga.get("scadenza", None)

        if pd.isna(valore):
            anomalie += 1
            continue

        try:
            data_scad = pd.to_datetime(valore).date()
        except Exception:
            anomalie += 1
            continue

        # Date anomale (tipo 1900/1909 ecc.)
        if data_scad.year < 1910:
            anomalie += 1
            continue

        diff = (data_scad - oggi).days

        if diff < 0:
            scaduti += 1
        elif diff <= 30:
            warning += 1
        else:
            ok += 1

    return {
        "totale_dpi": int(totale),
        "ok": int(ok),
        "warning": int(warning),
        "scaduti": int(scaduti),
        "anomalie": int(anomalie),
    }


def salva_cruscotto(cruscotto: dict) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    with open(CRUSCOTTO_JSON, "w", encoding="utf-8") as f:
        json.dump(cruscotto, f, indent=2, ensure_ascii=False)

    html = f"""<html>
<head><meta charset="UTF-8"><title>Cruscotto DPI</title></head>
<body>
<h1>Cruscotto DPI</h1>
<ul>
  <li>Totale DPI: {cruscotto['totale_dpi']}</li>
  <li>OK: {cruscotto['ok']}</li>
  <li>Warning (≤30gg): {cruscotto['warning']}</li>
  <li>Scaduti: {cruscotto['scaduti']}</li>
  <li>Anomalie: {cruscotto['anomalie']}</li>
</ul>
</body>
</html>
"""

    with open(CRUSCOTTO_HTML, "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    df = carica_dpi_da_csv()
    cruscotto = calcola_cruscotto(df)
    salva_cruscotto(cruscotto)
    print("[AGENTE0] Cruscotto rigenerato")
    print("[AGENTE0] JSON:", CRUSCOTTO_JSON)
    print("[AGENTE0] HTML:", CRUSCOTTO_HTML)


if __name__ == "__main__":
    main()
