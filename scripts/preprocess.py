#!/usr/bin/env python3
"""
Preprocess Bikeshed chapter includes.

Fixes applied per-chapter:
  1. GFM pipe tables → <table class=data> HTML
     (Bikeshed markdown has no GFM table support)
  2. \\| in table cells treated as literal pipe, not column separator
  3. Line-ending \\ (markdown hard line-break) → <br>
  4. Inter-chapter .md links rewritten:
       included chapters  → fragment links (#section-id)
       excluded chapters  → GitHub source URL
       ../schemas/…       → canonical schema URL (note: currently 404s per P1.1)
       ../../packages/…   → GitHub repo URL
       ../../../sdk/…     → GitHub repo URL

Usage:  python3 scripts/preprocess.py
  Reads chapters/*.md, writes chapters-processed/ copies.
"""

import re
import sys
from pathlib import Path

SRC = Path("chapters")
DST = Path("chapters-processed")
DST.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Link rewriting tables
# ---------------------------------------------------------------------------

# Chapters included in spec.bs and the fragment IDs Bikeshed generates for
# their H1 headings. Used to rewrite intra-spec cross-links to fragment refs.
INCLUDED_CHAPTERS: dict[str, str] = {
    "index.md": "#design-data-specification",
    "token-format.md": "#token-format",
    "taxonomy.md": "#taxonomy",
    "agent-surface.md": "#agent-readable-surface",
    "rules-excerpt.md": "#validation-rule-catalog-excerpt",
}

CANONICAL_SPEC = (
    "https://github.com/adobe/spectrum-design-data"
    "/blob/main/packages/design-data-spec/spec/"
)
CANONICAL_SCHEMAS = (
    "https://opensource.adobe.com/spectrum-design-data/schemas/v0/"
)
CANONICAL_REPO = "https://github.com/adobe/spectrum-design-data/blob/main/"


def _rewrite_link(match: re.Match) -> str:
    """Rewrite a single [text](url) markdown link."""
    text = match.group(1)
    url = match.group(2)

    # ---- inter-chapter .md links ----------------------------------------
    # Pattern: chapter.md  or  chapter.md#fragment
    m = re.match(r"^([a-z0-9_-]+\.md)(#[^\s)]*)?$", url, re.IGNORECASE)
    if m:
        chapter = m.group(1)
        fragment = m.group(2) or ""
        if chapter in INCLUDED_CHAPTERS:
            # Use fragment only for same-page link
            target = fragment if fragment else INCLUDED_CHAPTERS[chapter]
        else:
            target = CANONICAL_SPEC + chapter + fragment
        return f"[{text}]({target})"

    # ---- relative schema links  (any depth) ../schemas/… -----------------
    if re.search(r"^(\.\./)+schemas/", url):
        tail = re.sub(r"^(\.\./)+schemas/", "", url)
        return f"[{text}]({CANONICAL_SCHEMAS}{tail})"

    # ---- relative registry/package links  (any depth) ../../packages/… ---
    if re.search(r"^(\.\./)+packages/", url):
        tail = re.sub(r"^(\.\./)+", "", url)
        return f"[{text}]({CANONICAL_REPO}{tail})"

    # ---- relative SDK links  (any depth) ../../../sdk/… ------------------
    if re.search(r"^(\.\./)+sdk/", url):
        tail = re.sub(r"^(\.\./)+", "", url)
        return f"[{text}]({CANONICAL_REPO}{tail})"

    return match.group(0)  # leave unchanged


_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def rewrite_links(line: str) -> str:
    return _LINK_RE.sub(_rewrite_link, line)


# ---------------------------------------------------------------------------
# Table conversion
# ---------------------------------------------------------------------------

_PIPE_PLACEHOLDER = "\x00PIPE\x00"


def _split_cells(row: str) -> list[str]:
    """Split a table row on unescaped | and restore \\| as literal |."""
    # Protect escaped pipes
    escaped = row.replace("\\|", _PIPE_PLACEHOLDER)
    stripped = escaped.strip().strip("|")
    return [c.strip().replace(_PIPE_PLACEHOLDER, "|") for c in stripped.split("|")]


def parse_table(lines: list[str]) -> str:
    """Convert GFM table lines to <table class=data>."""
    rows = [_split_cells(ln) for ln in lines]
    if len(rows) < 2:
        return "\n".join(lines)

    header = rows[0]
    body = rows[2:]  # skip separator row

    th_cells = "".join(f"<th>{rewrite_links(h)}</th>" for h in header)
    thead = f"  <thead><tr>{th_cells}</tr></thead>"

    tbody_rows = []
    for row in body:
        padded = (row + [""] * len(header))[: len(header)]
        td_cells = "".join(f"<td>{rewrite_links(c)}</td>" for c in padded)
        tbody_rows.append(f"    <tr>{td_cells}</tr>")

    tbody = "  <tbody>\n" + "\n".join(tbody_rows) + "\n  </tbody>"
    return f'<table class="data">\n{thead}\n{tbody}\n</table>\n'


# ---------------------------------------------------------------------------
# Hard line-break conversion  (trailing \  →  <br>)
# ---------------------------------------------------------------------------

_HARD_BREAK_RE = re.compile(r"\\\s*$")


def convert_hard_breaks(line: str) -> str:
    """Convert markdown hard line-breaks (trailing backslash) to <br>."""
    return _HARD_BREAK_RE.sub("<br>", line)


# ---------------------------------------------------------------------------
# Main preprocessor
# ---------------------------------------------------------------------------

def preprocess(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    table_buf: list[str] = []
    in_table = False
    in_fence = False  # inside fenced code block — skip most transforms

    for line in lines:
        # Track fenced code blocks (``` or ~~~)
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            in_fence = not in_fence
            out.append(line)
            continue

        is_table_row = bool(re.match(r"^\s*\|", line))

        if is_table_row and not in_fence:
            table_buf.append(line.rstrip("\n"))
            in_table = True
        else:
            if in_table:
                out.append(parse_table(table_buf) + "\n")
                table_buf = []
                in_table = False

            if not in_fence:
                line = convert_hard_breaks(line)
                line = rewrite_links(line)
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
