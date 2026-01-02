from __future__ import annotations
import sys
from pathlib import Path

BOM = b"\xef\xbb\xbf"


def _write_utf8_no_bom(p: Path, text: str) -> None:
    p.write_bytes(text.encode("utf-8"))


def main(argv: list[str]) -> int:
    files = [a for a in argv[1:] if a.lower().endswith((".cmd", ".bat"))]
    for f in files:
        p = Path(f)
        if not p.is_file():
            continue
        b = p.read_bytes()
        if b.startswith(BOM):
            b = b[len(BOM) :]
        t = b.decode("utf-8", errors="replace")
        # normalizza a LF
        t = t.replace("\r\n", "\n").replace("\r", "\n")
        # poi porta a CRLF
        t = t.replace("\n", "\r\n")
        if not t.endswith("\r\n"):
            t += "\r\n"
        _write_utf8_no_bom(p, t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
