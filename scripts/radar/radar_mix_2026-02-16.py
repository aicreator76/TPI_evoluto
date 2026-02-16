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


def norm_id(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return str(s).strip()


def status_from_due(due, warn_days):
    if due is None or pd.isna(due):
        return "unknown", None
    d = pd.to_datetime(due, errors="coerce")
    if pd.isna(d):
        return "unknown", None
    # scarta date "1900-12-30" (tipico placeholder excel)
    if d.date() <= date(1901, 1, 1):
        return "unknown", None
    delta = (d.date() - date.today()).days
    if delta <= 0:
        return "expired", delta
    if delta <= warn_days:
        return "warning", delta
    return "ok", delta


def add_radar(df, due_col, prefix, warn_days):
    df[due_col] = pd.to_datetime(df[due_col], errors="coerce", dayfirst=True)
    sts, days = [], []
    for v in df[due_col]:
        st, dd = status_from_due(v, warn_days)
        sts.append(st)
        days.append(dd)
    df[f"{prefix}_status"] = sts
    df[f"{prefix}_days_to_due"] = days
    return df


def pick_join_key(df):
    # preferisci Matricola (N. SERIE), altrimenti Codice
    key1 = "Matricola                        (N. SERIE)"
    key2 = "Codice"
    if key1 in df.columns:
        return key1
    if key2 in df.columns:
        return key2
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev-xlsx", required=True, help="Excel revisione (scadenziario)")
    ap.add_argument("--life-xlsx", default="", help="Excel vita utile/anagrafica (opzionale)")
    ap.add_argument("--rev-sheet", default="0")
    ap.add_argument("--life-sheet", default="0")
    ap.add_argument("--header", type=int, default=3)
    ap.add_argument("--warn-days", type=int, default=60)
    ap.add_argument("--outdir", default=r"E:\CLONAZIONE\REPORT_DELTA\REPORTS")
    args = ap.parse_args()

    rev_sheet = int(args.rev_sheet) if str(args.rev_sheet).isdigit() else args.rev_sheet
    life_sheet = int(args.life_sheet) if str(args.life_sheet).isdigit() else args.life_sheet

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    base = f"TPI_RadarMIX_{stamp}"

    # --- REV
    rev = clean_excel(args.rev_xlsx, sheet=rev_sheet, header_guess=args.header)
    join_key_rev = pick_join_key(rev)
    if not join_key_rev:
        raise SystemExit("Nel file REV non trovo nÃ© 'Matricola (N. SERIE)' nÃ© 'Codice'.")

    rev[join_key_rev] = rev[join_key_rev].map(norm_id)

    if "Data scad verifica" not in rev.columns:
        raise SystemExit("Nel file REV non trovo 'Data scad verifica'.")

    rev = add_radar(rev, "Data scad verifica", "REV", args.warn_days)

    # --- LIFE (opzionale)
    merged = rev.copy()
    if args.life_xlsx:
        life = pd.read_excel(
            args.life_xlsx, sheet_name=life_sheet, engine="openpyxl"
        )  # spesso l'anagrafica Ã¨ piÃ¹ semplice
        life.columns = [str(c).strip() for c in life.columns]

        # prova chiavi
        join_key_life = None
        for k in ["Matricola", "Matricola (N. SERIE)", "N. SERIE", "Seriale", "Codice"]:
            if k in life.columns:
                join_key_life = k
                break
        if not join_key_life:
            raise SystemExit(
                "Nel file LIFE non trovo una colonna chiave (Matricola/Seriale/Codice)."
            )

        life[join_key_life] = life[join_key_life].map(norm_id)

        # trova colonna scadenza vita utile
        life_due_col = None
        for k in ["Scadenza", "Data scadenza", "Fine vita", "Expiry", "Expiration"]:
            if k in life.columns:
                life_due_col = k
                break
        if not life_due_col:
            raise SystemExit(
                "Nel file LIFE non trovo la colonna di scadenza (Scadenza/Fine vita...)."
            )

        life = add_radar(life, life_due_col, "LIFE", args.warn_days)

        merged = merged.merge(
            life[[join_key_life, life_due_col, "LIFE_status", "LIFE_days_to_due"]],
            left_on=join_key_rev,
            right_on=join_key_life,
            how="left",
        )
        # pulizia colonna chiave duplicata
        if join_key_life in merged.columns and join_key_life != join_key_rev:
            merged.drop(columns=[join_key_life], inplace=True, errors="ignore")
    else:
        # se non hai LIFE, usiamo la colonna "Scadenza" giÃ  nel REV, se presente
        if "Scadenza" in merged.columns:
            merged = add_radar(merged, "Scadenza", "LIFE", args.warn_days)
        else:
            merged["LIFE_status"] = "unknown"
            merged["LIFE_days_to_due"] = None

    # --- MIX: rischio se uno dei due Ã¨ expired/warning
    def mix(st_rev, st_life):
        if st_rev == "expired" or st_life == "expired":
            return "expired"
        if st_rev == "warning" or st_life == "warning":
            return "warning"
        if st_rev == "ok" and st_life == "ok":
            return "ok"
        return "unknown"

    merged["MIX_status"] = [
        mix(r, life_st) for r, life_st in zip(merged["REV_status"], merged["LIFE_status"])
    ]

    # output
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
        f.write("TPI RADAR MIX (REV + LIFE)\n")
        f.write("---------------------------\n")
        f.write(f"Generato: {datetime.now()}\n")
        f.write(f"Totale: {len(merged)}\n\n")
        f.write("REV (revisione)\n")
        f.write(f"  OK: {len(merged[merged['REV_status']=='ok'])}\n")
        f.write(f"  Warning: {len(merged[merged['REV_status']=='warning'])}\n")
        f.write(f"  Expired: {len(merged[merged['REV_status']=='expired'])}\n")
        f.write(f"  Unknown: {len(merged[merged['REV_status']=='unknown'])}\n\n")
        f.write("LIFE (fine vita)\n")
        f.write(f"  OK: {len(merged[merged['LIFE_status']=='ok'])}\n")
        f.write(f"  Warning: {len(merged[merged['LIFE_status']=='warning'])}\n")
        f.write(f"  Expired: {len(merged[merged['LIFE_status']=='expired'])}\n")
        f.write(f"  Unknown: {len(merged[merged['LIFE_status']=='unknown'])}\n\n")
        f.write("MIX (rischio complessivo)\n")
        f.write(f"  OK: {len(merged[merged['MIX_status']=='ok'])}\n")
        f.write(f"  Warning: {len(merged[merged['MIX_status']=='warning'])}\n")
        f.write(f"  Expired: {len(merged[merged['MIX_status']=='expired'])}\n")
        f.write(f"  Unknown: {len(merged[merged['MIX_status']=='unknown'])}\n")

    print("OK")
    print("OUTDIR:", outdir)
    print("FILES:", all_path.name, rev_exp.name, life_exp.name, mix_risk.name, rep_path.name)


if __name__ == "__main__":
    main()
