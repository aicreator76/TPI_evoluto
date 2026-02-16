from __future__ import annotations
import argparse
from datetime import datetime, date
from pathlib import Path
import pandas as pd


def clean_excel_rev(path: str, sheet=0, header_guess=3):
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


def norm_id(x):
    if x is None:
        return ""
    if isinstance(x, float) and pd.isna(x):
        return ""
    s = str(x).strip()
    return s


def status_from_due(due, warn_days):
    if due is None or pd.isna(due):
        return "unknown", None
    d = pd.to_datetime(due, errors="coerce", dayfirst=True)
    if pd.isna(d):
        return "unknown", None
    # scarta placeholder Excel 1900
    if d.date() <= date(1901, 1, 1):
        return "unknown", None
    delta = (d.date() - date.today()).days
    if delta <= 0:
        return "expired", delta
    if delta <= warn_days:
        return "warning", delta
    return "ok", delta


def add_radar(df, due_col, prefix, warn_days):
    if due_col not in df.columns:
        df[f"{prefix}_status"] = "unknown"
        df[f"{prefix}_days_to_due"] = None
        return df
    df[due_col] = pd.to_datetime(df[due_col], errors="coerce", dayfirst=True)
    sts, days = [], []
    for v in df[due_col].tolist():
        st, dd = status_from_due(v, warn_days)
        sts.append(st)
        days.append(dd)
    df[f"{prefix}_status"] = sts
    df[f"{prefix}_days_to_due"] = days
    return df


def pick_key_rev(df):
    k1 = "Matricola                        (N. SERIE)"
    k2 = "Codice"
    if k1 in df.columns:
        return k1
    if k2 in df.columns:
        return k2
    return None


def find_key_life(cols):
    # prova nomi tipici
    candidates = [
        "Matricola                        (N. SERIE)",
        "Matricola (N. SERIE)",
        "Matricola",
        "N. SERIE",
        "N. Serie",
        "Seriale",
        "Serie",
        "Codice",
        "ID",
        "Id",
    ]
    for c in candidates:
        if c in cols:
            return c
    # fallback: se c’è una colonna che contiene "matricol" o "serie" o "codice"
    low = {str(c).lower(): c for c in cols}
    for k in low:
        if "matricol" in k or "serie" in k or "codice" in k:
            return low[k]
    return None


def find_due_life(cols):
    candidates = ["Scadenza", "Data scadenza", "Fine vita", "Expiry", "Expiration"]
    for c in candidates:
        if c in cols:
            return c
    low = {str(c).lower(): c for c in cols}
    for k in low:
        if "scaden" in k or "fine" in k or "expiry" in k or "expir" in k:
            return low[k]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev-xlsx", required=True)
    ap.add_argument("--life-xlsx", required=True)
    ap.add_argument("--rev-sheet", default="0")
    ap.add_argument("--life-sheet", default="Import file")
    ap.add_argument("--rev-header", type=int, default=3)
    ap.add_argument("--life-header", type=int, default=7)  # riga 8 -> index 7
    ap.add_argument("--warn-days", type=int, default=60)
    ap.add_argument("--outdir", default=r"E:\CLONAZIONE\REPORT_DELTA\REPORTS")
    args = ap.parse_args()

    rev_sheet = int(args.rev_sheet) if str(args.rev_sheet).isdigit() else args.rev_sheet
    life_sheet = int(args.life_sheet) if str(args.life_sheet).isdigit() else args.life_sheet

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    base = f"TPI_RadarMIX_{stamp}"

    # REV (con pulizia header)
    rev = clean_excel_rev(args.rev_xlsx, sheet=rev_sheet, header_guess=args.rev_header)
    key_rev = pick_key_rev(rev)
    if not key_rev:
        raise SystemExit("REV: non trovo Matricola (N. SERIE) o Codice.")

    rev[key_rev] = rev[key_rev].map(norm_id)

    # Radar REV: revisione
    rev = add_radar(rev, "Data scad verifica", "REV", args.warn_days)

    # LIFE (header a riga 8)
    life = pd.read_excel(
        args.life_xlsx, sheet_name=life_sheet, header=int(args.life_header), engine="openpyxl"
    )
    life.columns = [str(c).strip() for c in life.columns]
    key_life = find_key_life(list(life.columns))
    if not key_life:
        raise SystemExit(f"LIFE: non trovo colonna chiave. Colonne: {list(life.columns)}")

    life[key_life] = life[key_life].map(norm_id)
    due_life = find_due_life(list(life.columns))
    if not due_life:
        raise SystemExit("LIFE: non trovo colonna scadenza (Scadenza/Fine vita/...).")

    life = add_radar(life, due_life, "LIFE", args.warn_days)

    merged = rev.merge(
        life[[key_life, due_life, "LIFE_status", "LIFE_days_to_due"]],
        left_on=key_rev,
        right_on=key_life,
        how="left",
    )
    if key_life in merged.columns and key_life != key_rev:
        merged.drop(columns=[key_life], inplace=True, errors="ignore")

    def mix(a, b):
        if a == "expired" or b == "expired":
            return "expired"
        if a == "warning" or b == "warning":
            return "warning"
        if a == "ok" and b == "ok":
            return "ok"
        return "unknown"

    merged["MIX_status"] = [mix(a, b) for a, b in zip(merged["REV_status"], merged["LIFE_status"])]

    all_path = outdir / f"{base}_ALL.csv"
    rev_exp = outdir / f"{base}_REV_EXPIRED.csv"
    life_exp = outdir / f"{base}_LIFE_EXPIRED.csv"
    mix_risk = outdir / f"{base}_MIX_RISK.csv"
    rep_path = outdir / f"{base}_REPORT.txt"

    merged.to_csv(all_path, index=False, encoding="utf-8-sig")
    merged[merged["REV_status"] == "expired"].to_csv(rev_exp, index=False, encoding="utf-8-sig")
    merged[merged["LIFE_status"] == "expired"].to_csv(life_exp, index=False, encoding="utf-8-sig")
    merged[merged["MIX_status"].isin(["expired", "warning"])].to_csv(
        mix_risk, index=False, encoding="utf-8-sig"
    )

    with rep_path.open("w", encoding="utf-8") as f:
        f.write("TPI RADAR MIX (REV + LIFE)\\n")
        f.write("---------------------------\\n")
        f.write(f"Generato: {datetime.now()}\\n")
        f.write(f"Totale: {len(merged)}\\n\\n")
        f.write("REV (revisione)\\n")
        f.write(f"  OK: {len(merged[merged['REV_status']=='ok'])}\\n")
        f.write(f"  Warning: {len(merged[merged['REV_status']=='warning'])}\\n")
        f.write(f"  Expired: {len(merged[merged['REV_status']=='expired'])}\\n")
        f.write(f"  Unknown: {len(merged[merged['REV_status']=='unknown'])}\\n\\n")
        f.write("LIFE (fine vita)\\n")
        f.write(f"  OK: {len(merged[merged['LIFE_status']=='ok'])}\\n")
        f.write(f"  Warning: {len(merged[merged['LIFE_status']=='warning'])}\\n")
        f.write(f"  Expired: {len(merged[merged['LIFE_status']=='expired'])}\\n")
        f.write(f"  Unknown: {len(merged[merged['LIFE_status']=='unknown'])}\\n\\n")
        f.write("MIX (rischio complessivo)\\n")
        f.write(f"  OK: {len(merged[merged['MIX_status']=='ok'])}\\n")
        f.write(f"  Warning: {len(merged[merged['MIX_status']=='warning'])}\\n")
        f.write(f"  Expired: {len(merged[merged['MIX_status']=='expired'])}\\n")
        f.write(f"  Unknown: {len(merged[merged['MIX_status']=='unknown'])}\\n")

    print("OK")
    print("OUTDIR:", outdir)
    print("FILES:", all_path.name, rev_exp.name, life_exp.name, mix_risk.name, rep_path.name)
    print("KEY_REV:", key_rev)
    print("KEY_LIFE:", key_life)
    print("DUE_LIFE:", due_life)


if __name__ == "__main__":
    main()
