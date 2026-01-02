from __future__ import annotations
import re
import sys
from pathlib import Path

BOM = b"\xef\xbb\xbf"
SKIP = re.compile(r"\.(png|jpg|jpeg|gif|pdf|zip|exe|apk)$", re.IGNORECASE)


def main(argv: list[str]) -> int:
    for f in argv[1:]:
        if not f:
            continue
        if f.lower().endswith(".csv"):
            continue
        if SKIP.search(f):
            continue
        p = Path(f)
        if not p.is_file():
            continue
        b = p.read_bytes()
        if b.startswith(BOM):
            p.write_bytes(b[len(BOM) :])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
