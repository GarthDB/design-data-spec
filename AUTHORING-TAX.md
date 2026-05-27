# Authoring tax notes — sub-issue #1011

Evaluation data for decision criterion #3 (authoring tax) in
[adobe/spectrum-design-data#1006](https://github.com/adobe/spectrum-design-data/issues/1006).

## What was converted

In `chapters/token-format.md` only (~316 lines). Five defined terms from plain bold
to Bikeshed autolink markup:

| Term | dfn site | Use-site conversions |
| ---- | -------- | -------------------- |
| `token` | line 9 | 2 (`[=token=]` on lines 5, 101) |
| `name object` | line 44 | 1 (`[=name object=]` on line 15) |
| `field catalog` | line 48 | 0 additional (only one occurrence in the chapter) |
| `value` | line 17 | 1 (`[=value=]` on lines 5, 101) |
| `alias` | line 99 | 1 (`[=alias=]` on lines 5, 18) |

**Total lines changed:** ~10 of 316 (~3%).

## Friction points encountered

1. **GFM pipe tables not supported** (CRITICAL). Bikeshed's `Markup Shorthands:
   markdown yes` does NOT include GFM pipe table support — confirmed by inspecting
   `bikeshed/markdown/markdown.py`. All ~130 table rows across the 4 chapters were
   rendered as raw `| ... |` text inside `<p>` tags.
   **Workaround**: `scripts/preprocess.py` converts pipe tables to `<table class=data>`
   HTML before Bikeshed processes the files. This is a mandatory build step; without it
   the spec is unreadable.
   **Migration cost**: All existing GFM tables must either (a) go through this
   preprocessor permanently, or (b) be manually rewritten as HTML tables.

2. **Nested list items needed 4-space indentation**, not 3 (Bikeshed markdown parser
   requirement). Lines 17–18 of token-format.md had `   * ...` (3-space) which caused
   fatal build errors. Changed to `    * ...` (4-space). This is a global compatibility
   risk: every markdown file must be audited for 3-space sub-lists.

2. **`<dfn>` inside a list item** causes "isn't indented enough" errors when on a
   3-space-indented `* ` bullet. Resolved by fixing the indentation (see above).

3. **`name-object` ID conflict**: The `## Name object` heading generates id
   `name-object`; `<dfn export>name object</dfn>` also generates that ID. Bikeshed
   deduplicates automatically but warns. In a production migration, explicit `id=`
   attributes on headings would resolve this.

4. **Multi-word dfn terms** (`name object`, `field catalog`) work cleanly with
   `[=name object=]` syntax — no extra markup needed at use sites.

5. **Biblio cross-refs** (`[[RFC2119]]`, `[[SEMVER]]`, `[[DISC735]]`): The chapters
   use plain markdown hyperlinks, not Bikeshed autolink syntax. Migrating them would
   require find-and-replace across all chapter files. RFC2119 and RFC8174 are in
   Bikeshed's built-in biblio database; SEMVER and DISC735 are registered in
   `biblio/spectrum.biblio.json` but show as "unused" because no chapter currently
   uses `[[SEMVER]]` syntax. Wiring these up is a one-time global find-replace,
   not per-definition work.

## Overall assessment

The `<dfn>` / `[=term=]` markup cost is **low per term** (~2 characters extra at
definition, ~4 characters extra at each use-site vs plain bold). The real cost is:
- Discovery: finding all use-sites of a term across 18+ chapter files.
- Indentation hygiene: a one-time audit to fix 3-space → 4-space sub-lists.
- ID conflicts: sections and dfns occasionally collide; explicit heading IDs would
  eliminate all such warnings.

Estimated one-time migration cost for all 18 spec chapters: ~4–8 hours of careful
find-and-replace plus an initial chapter-by-chapter indentation audit.

Per-chapter ongoing cost (new terms added): negligible once the pattern is established.
