import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
import pandas as pd

# carica .env manuale
env_path = Path(r"E:\CLONAZIONE\tpi_evoluto\scripts\radar\.env.proton_bridge")
if not env_path.exists():
    raise SystemExit("File .env.proton_bridge non trovato")

env = {}
for line in env_path.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip()

HOST = env["SMTP_HOST"]
PORT = int(env["SMTP_PORT"])
USER = env["SMTP_USER"]
PASS = env["SMTP_PASS"]
MAIL_FROM = env["MAIL_FROM"]
MAIL_TO_INTERNAL = env["MAIL_TO"]
MAIL_TO_CLIENT = env.get("MAIL_TO_CLIENT", "").strip()
REPORTS_DIR = Path(env["REPORTS_DIR"])


def latest(pattern: str) -> Path:
    files = sorted(REPORTS_DIR.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit(f"Nessun file trovato: {pattern}")
    return files[0]


def send(msg: EmailMessage):
    with smtplib.SMTP(HOST, PORT) as server:
        server.starttls()
        server.login(USER, PASS)
        server.send_message(msg)


# ultimi output
mix_csv = latest("TPI_RadarMIX_*_MIX_RISK.csv")
report_txt = latest("TPI_RadarMIX_*_REPORT.txt")
dash_pdf = latest("TPI_DashboardRischio_*.pdf")

now = datetime.now().strftime("%Y-%m-%d %H:%M")

# =========================
# 1) EMAIL INTERNA (FULL)
# =========================
msg_i = EmailMessage()
msg_i["Subject"] = f"TPI Radar MIX (INTERNO) - {now}"
msg_i["From"] = MAIL_FROM
msg_i["To"] = MAIL_TO_INTERNAL
msg_i.set_content(
    "Report automatico TPI Radar (INTERNO).\n"
    "- Allegato: MIX_RISK.csv (elenco completo rischio)\n"
    "- Allegato: REPORT.txt (riepilogo)\n"
    "\nCamelot – Sistema DPI"
)

msg_i.add_attachment(mix_csv.read_bytes(), maintype="text", subtype="csv", filename=mix_csv.name)
msg_i.add_attachment(
    report_txt.read_bytes(), maintype="text", subtype="plain", filename=report_txt.name
)

send(msg_i)

print("OK EMAIL INTERNA")
print("TO  :", MAIL_TO_INTERNAL)
print("CSV :", mix_csv.name)
print("REP :", report_txt.name)

# =========================
# 2) EMAIL CLIENTE (MINI)
# =========================
if MAIL_TO_CLIENT:
    df = pd.read_csv(mix_csv, encoding="utf-8-sig")
    total = len(df) if len(df) else 1

    counts = (
        df["MIX_status"].value_counts(dropna=False).to_dict() if "MIX_status" in df.columns else {}
    )
    exp = int(counts.get("expired", 0))
    warn = int(counts.get("warning", 0))
    unk = int(counts.get("unknown", 0))
    ok = int(counts.get("ok", 0))

    def pct(x):
        return round((x / total) * 100, 1)

    mini_lines = [
        f"Totale DPI analizzati: {total}",
        f"Critici (scaduti): {exp} ({pct(exp)}%)",
        f"Attenzione (entro soglia): {warn} ({pct(warn)}%)",
        f"Sconosciuti (dati incompleti): {unk} ({pct(unk)}%)",
        f"OK: {ok} ({pct(ok)}%)",
    ]
    mini_csv = (
        "KPI,Valore\n"
        + "\n".join(
            [
                f"Totale,{total}",
                f"Critici_scaduti,{pct(exp)}%",
                f"Attenzione_warn,{pct(warn)}%",
                f"Sconosciuti,{pct(unk)}%",
                f"OK,{pct(ok)}%",
            ]
        )
        + "\n"
    )

    msg_c = EmailMessage()
    msg_c["Subject"] = f"TPI Dashboard Rischio DPI - {now}"
    msg_c["From"] = MAIL_FROM
    msg_c["To"] = MAIL_TO_CLIENT
    msg_c.set_content(
        "Dashboard Rischio DPI (CLIENTE).\n\n"
        + "\n".join(mini_lines)
        + "\n\nNota: l’elenco completo e i dettagli restano nella versione interna.\n"
        "\nCamelot – Sistema DPI"
    )

    msg_c.add_attachment(
        dash_pdf.read_bytes(), maintype="application", subtype="pdf", filename=dash_pdf.name
    )
    msg_c.add_attachment(
        mini_csv.encode("utf-8-sig"), maintype="text", subtype="csv", filename="TPI_KPI_MINI.csv"
    )

    send(msg_c)

    print("OK EMAIL CLIENTE")
    print("TO  :", MAIL_TO_CLIENT)
    print("PDF :", dash_pdf.name)
    print("CSV :", "TPI_KPI_MINI.csv")
else:
    print("MAIL_TO_CLIENT non impostato: salto invio cliente.")
