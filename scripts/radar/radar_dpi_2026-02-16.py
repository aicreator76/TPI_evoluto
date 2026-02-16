from __future__ import annotations
import argparse
from datetime import datetime, date
from pathlib import Path
import pandas as pd


def clean_excel(path: str, sheet=0, header_guess=3):
    df = pd.read_excel(path, sheet_name=sheet, header=header_guess, engine="openpyxl")
    header_row = df.iloc[0].copy()

    new_cols = []
    for col in df.columns:
        val = header_row.get(col)
        if isinstance(val, str) and val.strip():
            new_cols.append(val.strip())
        else:
            new_cols.append(str(col).strip())

    df.columns = new_cols
    df = df.iloc[1:].copy()
    df = df.dropna(how="all")
    return df


def status_from_due(due, warn_days):
    if pd.isna(due):
        return "unknown", None
    d = pd.to_datetime(due, errors="coerce")
    if pd.isna(d):
        return "unknown", None
    delta = (d.date() - date.today()).days
    if delta <= 0:
        return "expired", delta
    if delta <= warn_days:
        return "warning", delta
    return "ok", delta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--sheet", default="0")
    ap.add_argument("--header", type=int, default=3)
    ap.add_argument("--warn-days", type=int, default=60)
    ap.add_argument("--outdir", default=r"E:\CLONAZIONE\REPORT_DELTA\REPORTS")
    args = ap.parse_args()

    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = clean_excel(args.xlsx, sheet=sheet, header_guess=args.header)

    if "Data scad verifica" not in df.columns:
        raise SystemExit("Colonna 'Data scad verifica' non trovata.")

    df["Data scad verifica"] = pd.to_datetime(df["Data scad verifica"], errors="coerce")

    statuses = []
    days = []
    for v in df["Data scad verifica"]:
        st, dd = status_from_due(v, args.warn_days)
        statuses.append(st)
        days.append(dd)

    df["tpi_status"] = statuses
    df["tpi_days_to_due"] = days

    expired = df[df["tpi_status"] == "expired"]
    warning = df[df["tpi_status"] == "warning"]

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    base = f"TPI_RadarDPI_{stamp}"

    all_path = outdir / f"{base}_ALL.csv"
    exp_path = outdir / f"{base}_EXPIRED.csv"
    due_path = outdir / f"{base}_DUE_{args.warn_days}D.csv"
    rep_path = outdir / f"{base}_REPORT.txt"

    df.to_csv(all_path, index=False, encoding="utf-8-sig")
    expired.to_csv(exp_path, index=False, encoding="utf-8-sig")
    pd.concat([expired, warning]).to_csv(due_path, index=False, encoding="utf-8-sig")

    with rep_path.open("w", encoding="utf-8") as f:
        f.write("TPI RADAR DPI\n")
        f.write("-----------------------\n")
        f.write(f"Generato: {datetime.now()}\n")
        f.write(f"Totale: {len(df)}\n")
        f.write(f"OK: {len(df[df['tpi_status']=='ok'])}\n")
        f.write(f"In scadenza: {len(warning)}\n")
        f.write(f"Scaduti: {len(expired)}\n")
        f.write(f"Senza data: {len(df[df['tpi_status']=='unknown'])}\n")

    print("OK")
    print("OUTDIR:", outdir)
    print("FILES:", all_path.name, exp_path.name, due_path.name, rep_path.name)


if __name__ == "__main__":
    main()
