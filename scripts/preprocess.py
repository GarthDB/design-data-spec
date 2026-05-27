#!/usr/bin/env python3
"""
Preprocess Bikeshed chapter includes: convert GFM pipe tables to HTML
tables so Bikeshed's markdown processor can render them correctly.

Usage: python3 scripts/preprocess.py
  Reads chapters/*.md, writes preprocessed copies to chapters-processed/
"""

import re
import sys
from pathlib import Path

SRC = Path("chapters")
DST = Path("chapters-processed")
DST.mkdir(exist_ok=True)


def parse_table(lines: list[str]) -> str:
    """Convert a list of GFM table lines to a Bikeshed <table class=data> block."""
    rows = []
    for line in lines:
        # Strip outer pipes, split on |, strip cell whitespace
        stripped = line.strip().strip("|")
        cells = [c.strip() for c in stripped.split("|")]
        rows.append(cells)

    if len(rows) < 2:
        return "\n".join(lines)

    header = rows[0]
    # Row 1 is the separator (--- | --- …) — skip it
    body = rows[2:]

    def wrap_inline(cell: str) -> str:
        """Leave inline content as-is — Bikeshed handles backticks/bold/links."""
        return cell

    th_cells = "".join(f"<th>{wrap_inline(h)}</th>" for h in header)
    thead = f"  <thead><tr>{th_cells}</tr></thead>"

    tbody_rows = []
    for row in body:
        # Pad or truncate to match header width
        padded = row + [""] * max(0, len(header) - len(row))
        padded = padded[: len(header)]
        td_cells = "".join(f"<td>{wrap_inline(c)}</td>" for c in padded)
        tbody_rows.append(f"    <tr>{td_cells}</tr>")

    tbody = "  <tbody>\n" + "\n".join(tbody_rows) + "\n  </tbody>"

    return f'<table class="data">\n{thead}\n{tbody}\n</table>\n'


def preprocess(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    table_buf: list[str] = []
    in_table = False

    for line in lines:
        is_table_line = bool(re.match(r"^\s*\|", line))

        if is_table_line:
            table_buf.append(line.rstrip("\n"))
            in_table = True
        else:
            if in_table:
                out.append(parse_table(table_buf) + "\n")
                table_buf = []
                in_table = False
            out.append(line)

    if in_table and table_buf:
        out.append(parse_table(table_buf) + "\n")

    return "".join(out)


def main() -> None:
    sources = sorted(SRC.glob("*.md"))
    if not sources:
        print(f"No .md files found in {SRC}/", file=sys.stderr)
        sys.exit(1)

    for src in sources:
        dst = DST / src.name
        original = src.read_text(encoding="utf-8")
        processed = preprocess(original)
        dst.write_text(processed, encoding="utf-8")
        changed = original != processed
        print(f"{'  changed' if changed else 'unchanged'}: {src.name} -> {dst}")


if __name__ == "__main__":
    main()
