import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime

# carica .env manuale
env_path = Path(r"E:\CLONAZIONE\tpi_evoluto\scripts\radar\.env.proton_bridge")
if not env_path.exists():
    raise SystemExit("File .env.proton_bridge non trovato")

env = {}
for line in env_path.read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()

HOST = env["SMTP_HOST"]
PORT = int(env["SMTP_PORT"])
USER = env["SMTP_USER"]
PASS = env["SMTP_PASS"]
MAIL_FROM = env["MAIL_FROM"]
MAIL_TO = env["MAIL_TO"]
REPORTS_DIR = Path(env["REPORTS_DIR"])

# prende ultimo report MIX
reports = sorted(
    REPORTS_DIR.glob("TPI_RadarMIX_*_MIX_RISK.csv"), key=lambda x: x.stat().st_mtime, reverse=True
)
if not reports:
    raise SystemExit("Nessun file MIX_RISK trovato")

latest = reports[0]

msg = EmailMessage()
msg["Subject"] = f"TPI Radar MIX Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
msg["From"] = MAIL_FROM
msg["To"] = MAIL_TO
msg.set_content("Report automatico TPI Radar allegato.\n\nCamelot – Sistema DPI")

with open(latest, "rb") as f:
    msg.add_attachment(f.read(), maintype="text", subtype="csv", filename=latest.name)

with smtplib.SMTP(HOST, PORT) as server:
    server.starttls()
    server.login(USER, PASS)
    server.send_message(msg)

print("OK EMAIL")
print("FROM:", MAIL_FROM)
print("TO  :", MAIL_TO)
print("FILE:", latest.name)
