#!/usr/bin/env python3
"""
Preprocess Bikeshed chapter includes.

Fixes applied per-chapter (in order applied):
  1. GFM pipe tables → <table class=data> HTML
     (Bikeshed markdown has no GFM table support)
  2. \\| in table cells treated as literal pipe, not column separator
  3. Line-ending \\ (markdown hard line-break) → <br>
  4. \\[[label](url)] escaped-bracket links → [<a href="url">label</a>]
     (Bikeshed interprets [[ as biblio-ref syntax, corrupting RFC citations)
  5. Inter-chapter .md links rewritten:
       included chapters  → fragment links (#section-id)
       excluded chapters  → GitHub source URL
       ../schemas/…       → canonical schema URL (note: currently 404s per P1.1)
       ../fields/…        → GitHub repo URL (packages/design-data-spec/fields/)
       ../../packages/…   → GitHub repo URL
       ../../../sdk/…     → GitHub repo URL
       any other ../…     → resolved relative to spec/ and mapped to GitHub
  6. **text** (bold) → <strong>text</strong>
     (pre-converts bold so Bikeshed can handle **`code`** combos correctly)

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
# Constants
# ---------------------------------------------------------------------------

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

# Base path segments from which chapters are authored
_SPEC_BASE = ["packages", "design-data-spec", "spec"]

# ---------------------------------------------------------------------------
# Link rewriting
# ---------------------------------------------------------------------------

def _resolve_relative(url: str) -> str:
    """Resolve a relative ../… URL to a GitHub permalink."""
    nlevels = len(re.findall(r"\.\./", url))
    rest = re.sub(r"^(\.\./)+", "", url)
    base = _SPEC_BASE[: max(0, len(_SPEC_BASE) - nlevels)]
    parts = base + ([rest] if rest else [])
    return CANONICAL_REPO + "/".join(parts)


def _rewrite_link(match: re.Match) -> str:
    text = match.group(1)
    url = match.group(2)

    # inter-chapter .md links
    m = re.match(r"^([a-z0-9_-]+\.md)(#[^\s)]*)?$", url, re.IGNORECASE)
    if m:
        chapter, fragment = m.group(1), m.group(2) or ""
        if chapter in INCLUDED_CHAPTERS:
            target = fragment if fragment else INCLUDED_CHAPTERS[chapter]
        else:
            target = CANONICAL_SPEC + chapter + fragment
        return f"[{text}]({target})"

    # relative schema links
    if re.search(r"^(\.\./)+schemas/", url):
        tail = re.sub(r"^(\.\./)+schemas/", "", url)
        return f"[{text}]({CANONICAL_SCHEMAS}{tail})"

    # relative package/registry links
    if re.search(r"^(\.\./)+packages/", url):
        tail = re.sub(r"^(\.\./)+", "", url)
        return f"[{text}]({CANONICAL_REPO}{tail})"

    # relative SDK links
    if re.search(r"^(\.\./)+sdk/", url):
        tail = re.sub(r"^(\.\./)+", "", url)
        return f"[{text}]({CANONICAL_REPO}{tail})"

    # catch-all for any remaining ../… relative links
    if re.match(r"^(\.\./)+", url):
        return f"[{text}]({_resolve_relative(url)})"

    return match.group(0)


_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def rewrite_links(line: str) -> str:
    return _LINK_RE.sub(_rewrite_link, line)


# ---------------------------------------------------------------------------
# Escaped-bracket link conversion  \[label](url)] → [<a href>label</a>]
# ---------------------------------------------------------------------------

_ESC_BRACKET_RE = re.compile(r'\\\[\[([^\]]+)\]\(([^)]+)\)\]')


def convert_escaped_bracket_links(line: str) -> str:
    """Convert \\[label](url)] to [<a href="url">label</a>].

    Bikeshed treats [[ as a biblio-ref opener, so \\[[RFC2119](url)]
    gets corrupted. Pre-rendering these as explicit HTML avoids that.
    """
    return _ESC_BRACKET_RE.sub(
        lambda m: f'[<a href="{m.group(2)}">{m.group(1)}</a>]', line
    )


# ---------------------------------------------------------------------------
# Bold conversion  **text** → <strong>text</strong>
# ---------------------------------------------------------------------------

_BOLD_RE = re.compile(r'\*\*(.+?)\*\*')


def convert_bold(line: str) -> str:
    """Pre-convert **bold** to <strong> so Bikeshed handles **`code`** correctly.

    Bikeshed processes backticks before bold, leaving **<code>…</code>**
    unparseable as bold. Converting bold first fixes the ordering.
    """
    return _BOLD_RE.sub(r'<strong>\1</strong>', line)


# ---------------------------------------------------------------------------
# Hard line-break  trailing \\ → <br>
# ---------------------------------------------------------------------------

_HARD_BREAK_RE = re.compile(r"\\\s*$")


def convert_hard_breaks(line: str) -> str:
    return _HARD_BREAK_RE.sub("<br>", line)


# ---------------------------------------------------------------------------
# Table conversion
# ---------------------------------------------------------------------------

_PIPE_PLACEHOLDER = "\x00PIPE\x00"


def _split_cells(row: str) -> list[str]:
    escaped = row.replace("\\|", _PIPE_PLACEHOLDER)
    stripped = escaped.strip().strip("|")
    return [c.strip().replace(_PIPE_PLACEHOLDER, "|") for c in stripped.split("|")]


def parse_table(lines: list[str]) -> str:
    rows = [_split_cells(ln) for ln in lines]
    if len(rows) < 2:
        return "\n".join(lines)

    header = rows[0]
    body = rows[2:]

    def cell(content: str, tag: str) -> str:
        c = rewrite_links(content)
        c = convert_escaped_bracket_links(c)
        c = convert_bold(c)
        return f"<{tag}>{c}</{tag}>"

    th_cells = "".join(cell(h, "th") for h in header)
    thead = f"  <thead><tr>{th_cells}</tr></thead>"

    tbody_rows = []
    for row in body:
        padded = (row + [""] * len(header))[: len(header)]
        td_cells = "".join(cell(c, "td") for c in padded)
        tbody_rows.append(f"    <tr>{td_cells}</tr>")

    tbody = "  <tbody>\n" + "\n".join(tbody_rows) + "\n  </tbody>"
    return f'<table class="data">\n{thead}\n{tbody}\n</table>\n'


# ---------------------------------------------------------------------------
# Main preprocessor
# ---------------------------------------------------------------------------

def preprocess(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    table_buf: list[str] = []
    in_table = False
    in_fence = False

    for line in lines:
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
                line = convert_escaped_bracket_links(line)
                line = convert_bold(line)
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
