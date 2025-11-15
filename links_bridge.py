from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal, List
import re

# ====== Costanti cartelle ======
# File .url: restano sotto Downloads\url_farm (come prima)
BASE_DOWNLOADS = Path.home() / "Downloads" / "url_farm"
SHORT_DIR = BASE_DOWNLOADS / "url corti"
LONG_DIR = BASE_DOWNLOADS / "url lunghi"

# Log unico del Link Hub
LINKHUB_BASE = Path(r"C:\url_farm")
LOG_PATH = LINKHUB_BASE / "linkhub.log"

for d in (BASE_DOWNLOADS, SHORT_DIR, LONG_DIR, LINKHUB_BASE):
    d.mkdir(parents=True, exist_ok=True)


# ====== Standard TPI: nome file + log ======
def new_tpi_url_name(name: str) -> str:
    """
    Trasforma qualsiasi nome in:
    NOMELOGICO_YYYYMMDD_HHMM
    """
    base = re.sub(r"[^\w-]", "_", name or "").strip("_")
    if not base:
        base = "link"
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{base}_{ts}"


def write_link_log(source: str, type_: str, name: str, url: str) -> None:
    """
    Appende una riga a C:\\url_farm\\linkhub.log
    """
    try:
        LINKHUB_BASE.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] SOURCE={source} TYPE={type_} NAME={name} URL={url}"
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # Niente crash se il log fallisce
        pass


def read_url_from_file(path: Path) -> str:
    try:
        for line in path.read_text(encoding="ascii", errors="ignore").splitlines():
            if line.startswith("URL="):
                return line[4:].strip()
    except Exception:
        pass
    return ""


def make_url_file(folder: Path, name: str, url: str, type_: str, source: str) -> Path:
    """
    Crea il file .url con standard TPI + log.
    """
    folder.mkdir(parents=True, exist_ok=True)
    fname = new_tpi_url_name(name)
    path = folder / f"{fname}.url"
    content = f"[InternetShortcut]\r\nURL={url}\r\n"
    path.write_text(content, encoding="ascii")
    write_link_log(source=source, type_=type_, name=fname, url=url)
    return path


# ====== Modelli Pydantic ======
class LinkIn(BaseModel):
    name: Optional[str] = None
    url: str
    type: Literal["corto", "lungo"] = "lungo"


class LinkOut(BaseModel):
    ok: bool
    path: str
    name: str
    url: str
    type: Literal["corto", "lungo"]


class LinkEntry(BaseModel):
    name: str
    type: Literal["corto", "lungo"]
    url: str
    file: str


# ====== FastAPI app ======
app = FastAPI(title="TPI Link Bridge", version="1.0.0")


@app.post("/links", response_model=LinkOut)
def create_link(link: LinkIn):
    """
    Crea un file .url (corto/lungo) con standard TPI e mette una riga nel log.
    """
    if not link.url or not link.url.lower().startswith("http"):
        raise HTTPException(
            status_code=400, detail="Campo 'url' deve iniziare con http/https."
        )

    folder = SHORT_DIR if link.type == "corto" else LONG_DIR

    try:
        path = make_url_file(
            folder=folder,
            name=link.name or "link",
            url=link.url,
            type_=link.type,
            source="API",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Errore creazione file: {exc}")

    return LinkOut(
        ok=True,
        path=str(path),
        name=path.stem,
        url=link.url,
        type=link.type,
    )


@app.get("/links", response_model=List[LinkEntry])
def list_links():
    """
    Indice JSON di tutti i link in:
      - url corti
      - url lunghi
    Serve da base per il futuro TPI Link Hub online.
    """
    items: List[LinkEntry] = []

    for folder, type_ in ((SHORT_DIR, "corto"), (LONG_DIR, "lungo")):
        if not folder.exists():
            continue
        for f in sorted(folder.glob("*.url")):
            url = read_url_from_file(f)
            items.append(
                LinkEntry(
                    name=f.stem,
                    type=type_,
                    url=url,
                    file=str(f),
                )
            )

    return items
