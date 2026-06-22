# Task 4 Report — Journal Articles Section Generator

## What was built

**`tools/build_journal_sections.py`** — a CLI tool and importable module that:

1. Loads the journal catalog via `tools/lib_catalog.py:load_catalog`.
2. Groups records by `subdomain_page`.
3. For each page, renders three HTML fragments:
   - `render_tab_button()` — a `<button data-p="journal">` with a teal dot matching the `--lit` CSS variable.
   - `render_styles()` — a `<style data-journal-css>` block scoped to `.ja-*` class names, visually consistent with the existing page aesthetic (paper2 cards, muted meta in JetBrains Mono, abstract block with a `--lit` left accent border on `--lit-soft` background, native `<details>` answers styled as small teal buttons).
   - `render_panel(records)` — a `<section class="panel" id="journal">` with articles sorted by year desc then title asc. Each article card contains: citation line (title bold, meta in `ja-meta`), abstract block, and MCQs with A–D option lists and `<details class="ja-ans">` for self-testing.
4. Injects these fragments into the page HTML with idempotency markers.

## Anchor-finding approach

**Tab button insertion**: Regex-locates the `<div ... id="tabrow">` open tag, then finds the first `</div>` after it — that's the closing of the tabrow div. The tab marker block is inserted immediately before that `</div>`. On re-runs, the `<!-- JOURNAL-TAB:START -->…<!-- JOURNAL-TAB:END -->` region is replaced via `re.sub` with `DOTALL`.

**Panel insertion**: Regex-locates `</div>\s*</main>` — the closing of `main > .wrap` — and inserts the panel region immediately before it. On re-runs, `<!-- JOURNAL-ARTICLES:START -->…<!-- JOURNAL-ARTICLES:END -->` is replaced in place.

**Template guard**: If a page has no `id="tabrow"` div, or no `<main>` element, the tool prints a warning and returns `False` without modifying the file. This prevents corrupting non-conforming pages.

## Verification output (surgery pilot)

```
Processing 1 page(s)…
  [OK]   physical-health/surgery_anesthesia_hub.html → 10 article(s) injected
Done. 1 page(s) updated, 0 page(s) skipped.
```

- Marker count: `grep -c "JOURNAL-ARTICLES:START\|JOURNAL-TAB:START"` → **2** (1 each)
- Re-run marker count: **2** (unchanged — idempotent)
- `html.parser.HTMLParser().feed(content)` → **"parsed ok"** (no exception)
- `grep -c "const Q=\["` → **1** (original MCQ Test Bank JS untouched)
- `grep -c "Show answer"` → **30** (10 articles × 3 MCQs each)
- `grep -c "ja-article"` → **11** (10 `div.ja-article` blocks + 1 `.ja-article` in CSS)
- Tab button landed at line 145; panel started at line 627; `</div></main>` at line 1282.

## Page-template assumptions (rollout concerns)

1. **`id="tabrow"` detection**: The regex matches `id="tabrow"` inside a `<div>`. If a future page uses a different element (`<ul>`, `<nav>`) or quotes the id differently, the guard will fire and skip the page (safe, but needs manual adjustment).

2. **Single `</div></main>` anchor**: The tool finds the *first* `</div>\s*</main>` in the file. All current subdomain pages use the pattern `<main><div class="wrap">…</div></main>` with no nested `</div></main>` sequences, but if a future page has such a sequence (e.g., a deeply nested closing that inadvertently matches), the panel could be inserted in the wrong location. A more robust alternative would be to track nesting depth from `<main>`, but this would require a proper parser.

3. **`<main>` with inline `<div class="wrap">`**: The current template uses `<main><div class="wrap">` on a single line (line 152 in surgery). The tool only checks for `<main>` and relies on the `</div></main>` pattern for insertion. Pages that use `<main class="...">` or split `<div class="wrap">` across multiple lines will still work, but pages that don't use `.wrap` inside `<main>` (if any) would insert the panel at the wrong nesting level — visually acceptable but semantically wrong. Not a concern for current pages.

4. **`</div></main>` pattern**: The pattern allows `\s*` between the two tags, so both `</div></main>` (single line) and `</div>\n</main>` (two lines) are handled. The surgery page uses single-line `</div></main>` (confirmed at line 622 pre-injection, 1282 post-injection).

5. **CSS variable dependency**: The `render_styles()` block uses `var(--lit)`, `var(--lit-soft)`, `var(--paper2)`, `var(--muted)`, `var(--shadow)`, `var(--ink)`, `var(--ink2)`, `var(--line)`, `var(--good)`, and `var(--paper)`. All are declared in `:root` in the surgery hub. If other subdomain pages use different variable names for the teal accent colour, the abstract left-border and dot colour would fall back to `initial`. Visually safe but potentially unstyled. Recommend auditing `:root` in each target page before full rollout.
