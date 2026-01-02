from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DATE_HINT = re.compile(r"(date|data|scad|scaden|expiry|exp)", re.IGNORECASE)
MARKERS = ("<<<<<<<", ">>>>>>>", "=======")


@dataclass
class Issue:
    row: int
    kind: str
    detail: str


@dataclass
class Summary:
    input_path: str
    detected_encoding: str
    delimiter: str
    headers: List[str]
    headers_normalized: List[str]
    row_count: int
    empty_lines: int
    inconsistent_rows: int
    marker_hits: int
    date_columns: List[str]
    date_parse_failures: Dict[str, int]
    issues_sample: List[Issue]
    normalized_path: Optional[str] = None


def repo_root() -> Path:
    # .../ops/agente0/step1_ingest_dpi_csv.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def normalize_header(h: str) -> str:
    h = h.strip().lower()
    h = re.sub(r"\s+", "_", h)
    h = re.sub(r"[^a-z0-9_]+", "", h)
    h = re.sub(r"_+", "_", h).strip("_")
    return h or "col"


def sniff_csv(sample: str) -> Tuple[str, csv.Dialect]:
    """
    mypy/typeshed: csv.Sniffer.sniff() a volte è tipizzato come type[Dialect].
    Qui lo rendiamo robusto: se arriva una classe, la istanziamo.
    """
    sniffer = csv.Sniffer()
    try:
        dialect_any: Any = sniffer.sniff(sample)
    except csv.Error:
        dialect_any = csv.get_dialect("excel")

    if isinstance(dialect_any, type):
        try:
            dialect_any = dialect_any()
        except Exception:
            dialect_any = csv.get_dialect("excel")

    dialect = dialect_any  # runtime ok, typing gestito sopra
    delim = getattr(dialect, "delimiter", ",") or ","
    return str(delim), dialect


def parse_date_like(value: str) -> bool:
    v = value.strip()
    if not v:
        return True
    fmts = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y.%m.%d")
    for f in fmts:
        try:
            datetime.strptime(v, f)
            return True
        except ValueError:
            pass
    return False


def write_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(p: Path, s: Summary) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append("# Agente0 Step1 — Ingest CSV\n")
    lines.append(f"- Input: `{s.input_path}`")
    lines.append(f"- Encoding: `{s.detected_encoding}`")
    lines.append(f"- Delimiter: `{s.delimiter}`")
    lines.append(f"- Rows: **{s.row_count}** (empty lines: {s.empty_lines})")
    lines.append(f"- Inconsistent rows: **{s.inconsistent_rows}**")
    lines.append(f"- Merge markers hits: **{s.marker_hits}**")

    if s.date_columns:
        lines.append(f"- Date-like columns: `{', '.join(s.date_columns)}`")
        lines.append("- Date parse failures:")
        for k, v in s.date_parse_failures.items():
            lines.append(f"  - `{k}`: **{v}**")

    if s.normalized_path:
        lines.append(f"- Normalized CSV: `{s.normalized_path}`")

    lines.append("\n## Headers\n")
    for a, b in zip(s.headers, s.headers_normalized):
        lines.append(f"- `{a}` → `{b}`")

    lines.append("\n## Issues sample\n")
    if not s.issues_sample:
        lines.append("- none")
    else:
        for it in s.issues_sample[:30]:
            lines.append(f"- row {it.row} [{it.kind}] {it.detail}")

    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(repo_root() / "data" / "dpi_import.csv"))
    ap.add_argument("--write-normalized", action="store_true")
    args = ap.parse_args(argv[1:])

    inp = Path(args.input)
    if not inp.is_file():
        raise SystemExit(f"Input not found: {inp}")

    raw = inp.read_bytes()
    enc = "utf-8"
    if raw.startswith(b"\xef\xbb\xbf"):
        enc = "utf-8-sig"

    text = raw.decode(enc, errors="replace")
    sample = text[:4096]
    delim, dialect = sniff_csv(sample)

    reader = csv.reader(text.splitlines(), dialect)
    headers: List[str] = []
    headers_norm: List[str] = []
    issues: List[Issue] = []
    row_count = 0
    empty_lines = 0
    inconsistent = 0
    marker_hits = 0

    date_cols: List[str] = []
    date_fail: Dict[str, int] = {}

    normalized_out: Optional[Path] = None
    out_writer: Any | None = None  # csv.writer non è un type (mypy)
    out_fh = None

    for i, row in enumerate(reader, start=1):
        if not row or all(not c.strip() for c in row):
            empty_lines += 1
            continue

        if any(any(m in (c or "") for m in MARKERS) for c in row):
            marker_hits += 1

        if not headers:
            headers = [c.strip() for c in row]
            headers_norm = [normalize_header(c) for c in headers]

            seen: Dict[str, int] = {}
            fixed: List[str] = []
            for h in headers_norm:
                n = seen.get(h, 0)
                seen[h] = n + 1
                fixed.append(h if n == 0 else f"{h}_{n+1}")
            headers_norm = fixed

            date_cols = [h for h in headers_norm if DATE_HINT.search(h)]
            for h in date_cols:
                date_fail[h] = 0

            if args.write_normalized:
                normalized_out = repo_root() / "reports" / "agente0" / "normalized_dpi_import.csv"
                normalized_out.parent.mkdir(parents=True, exist_ok=True)
                out_fh = normalized_out.open("w", encoding="utf-8", newline="\n")
                out_writer = csv.writer(
                    out_fh,
                    delimiter=",",
                    lineterminator="\n",
                    quoting=csv.QUOTE_MINIMAL,
                )
                out_writer.writerow(headers_norm)
            continue

        row_count += 1

        if len(row) != len(headers):
            inconsistent += 1
            if len(issues) < 50:
                issues.append(
                    Issue(row=i, kind="columns", detail=f"expected {len(headers)} got {len(row)}")
                )
            if len(row) < len(headers):
                row = row + [""] * (len(headers) - len(row))
            else:
                row = row[: len(headers)]

        if date_cols:
            for idx, h in enumerate(headers_norm):
                if h in date_cols and idx < len(row):
                    if not parse_date_like(row[idx]):
                        date_fail[h] = date_fail.get(h, 0) + 1
                        if len(issues) < 50:
                            issues.append(Issue(row=i, kind="date", detail=f"{h}='{row[idx]}'"))

        if out_writer:
            out_writer.writerow(row)

    if out_fh:
        out_fh.close()

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rep_dir = repo_root() / "reports" / "agente0"
    js = rep_dir / f"step1_summary_{ts}.json"
    md = rep_dir / f"step1_summary_{ts}.md"

    summary = Summary(
        input_path=str(inp),
        detected_encoding=enc,
        delimiter=delim,
        headers=headers,
        headers_normalized=headers_norm,
        row_count=row_count,
        empty_lines=empty_lines,
        inconsistent_rows=inconsistent,
        marker_hits=marker_hits,
        date_columns=date_cols,
        date_parse_failures=date_fail,
        issues_sample=issues,
        normalized_path=str(normalized_out) if normalized_out else None,
    )

    write_json(js, {**asdict(summary), "issues_sample": [asdict(x) for x in issues]})
    write_md(md, summary)

    print(f"OK: wrote {js}")
    print(f"OK: wrote {md}")
    if normalized_out:
        print(f"OK: wrote {normalized_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
