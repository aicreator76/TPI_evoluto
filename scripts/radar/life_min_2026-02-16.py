import pandas as pd
from pathlib import Path
import sys

infile = r"E:\CLONAZIONE\REPORT_DELTA\INTAKE\SCADENZIARIO_REV.xlsx"
outdir = Path(r"E:\CLONAZIONE\REPORT_DELTA\REPORTS")
stamp = pd.Timestamp.now().strftime("%Y-%m-%d_%H%M")
outxlsx = outdir / f"TPI_LIFE_MIN_{stamp}.xlsx"
outcsv = outdir / f"TPI_LIFE_MIN_{stamp}.csv"

# leggi REV come fai già (header=3 + prima riga con nomi reali)
df = pd.read_excel(infile, sheet_name=0, header=3, engine="openpyxl")
hdr = df.iloc[0].copy()

new_cols = []
for c in df.columns:
    v = hdr.get(c)
    new_cols.append(v.strip() if isinstance(v, str) and v.strip() else str(c).strip())

df.columns = new_cols
df = df.iloc[1:].dropna(how="all").copy()

# chiave
key_candidates = ["Matricola                        (N. SERIE)", "Codice"]
key = next((k for k in key_candidates if k in df.columns), None)
if not key:
    print("ERRORE: nel REV non trovo Matricola (N. SERIE) o Codice.")
    print("COLONNE:", list(df.columns))
    sys.exit(2)

# scadenza vita: se c'è 'Scadenza' la usiamo (migliore base reale)
life_due_col = "Scadenza" if "Scadenza" in df.columns else None

# data produzione: prova su Unnamed: 15 (spesso è data), altrimenti Anno di costruzione
prod_date_col = None
if "Unnamed: 15" in df.columns:
    prod_date_col = "Unnamed: 15"
elif "Data di produzione" in df.columns:
    prod_date_col = "Data di produzione"
elif "Anno di costruzione" in df.columns:
    prod_date_col = "Anno di costruzione"

life = pd.DataFrame()
life["Matricola                        (N. SERIE)"] = df[key].astype(str).str.strip()

# produttore/modello/categoria (se presenti)
if "Marca" in df.columns:
    life["Produttore"] = df["Marca"]
if "Modello" in df.columns:
    life["Modello"] = df["Modello"]
if "Articolo" in df.columns:
    life["Categoria"] = df["Articolo"]

# produzione
if prod_date_col:
    if prod_date_col == "Anno di costruzione":
        y = pd.to_numeric(df[prod_date_col], errors="coerce").astype("Int64")
        life["Data di produzione"] = pd.to_datetime(y.astype(str) + "-01-01", errors="coerce")
    else:
        life["Data di produzione"] = pd.to_datetime(
            df[prod_date_col], errors="coerce", dayfirst=True
        )

# scadenza
if life_due_col:
    life["Scadenza"] = pd.to_datetime(df[life_due_col], errors="coerce", dayfirst=True)
else:
    # fallback: 10 anni da produzione (se presente)
    prod = pd.to_datetime(
        life.get("Data di produzione", pd.Series([pd.NaT] * len(df))), errors="coerce"
    )
    life["Scadenza"] = prod + pd.DateOffset(years=10)

# pulizia righe senza seriale
life = life[
    life["Matricola                        (N. SERIE)"].ne("")
    & life["Matricola                        (N. SERIE)"].ne("nan")
].copy()

outdir.mkdir(parents=True, exist_ok=True)
life.to_excel(outxlsx, index=False)
life.to_csv(outcsv, index=False, encoding="utf-8-sig")

print("OK LIFE_MIN")
print("XLSX:", outxlsx)
print("CSV :", outcsv)
print("RIGHE:", len(life))
print("COLONNE:", list(life.columns))
