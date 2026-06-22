#!/usr/bin/env python3
"""
build_journal_sections.py — Inject Journal Articles sections into ABVP hub subdomain pages.

Usage:
    python3 tools/build_journal_sections.py [--page RELPATH]

With --page, only that page is processed.
Without --page, every distinct subdomain_page that has ≥1 record is processed.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo layout
# ---------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOLS_DIR.parent
_CATALOG_PATH = _TOOLS_DIR / "journal-catalog.json"

sys.path.insert(0, str(_TOOLS_DIR))
from lib_catalog import load_catalog  # noqa: E402

# ---------------------------------------------------------------------------
# Idempotency markers
# ---------------------------------------------------------------------------
TAB_START = "<!-- JOURNAL-TAB:START -->"
TAB_END = "<!-- JOURNAL-TAB:END -->"
PANEL_START = "<!-- JOURNAL-ARTICLES:START -->"
PANEL_END = "<!-- JOURNAL-ARTICLES:END -->"

# Letter labels
_LETTERS = ["A", "B", "C", "D"]


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _e(text: str) -> str:
    """HTML-escape a string."""
    return html.escape(str(text), quote=True)


def _abstract_html(text: str) -> str:
    """HTML-escape abstract and convert blank lines / double newlines to <br><br>."""
    escaped = html.escape(str(text), quote=False)
    # Normalise CRLF → LF, then replace blank-line sequences
    escaped = escaped.replace("\r\n", "\n").replace("\r", "\n")
    escaped = re.sub(r"\n{2,}", "<br><br>", escaped)
    # Single newlines become a space (soft wrap)
    escaped = escaped.replace("\n", " ")
    return escaped.strip()


# ---------------------------------------------------------------------------
# render_* functions
# ---------------------------------------------------------------------------

def render_tab_button() -> str:
    """Return the tab button HTML for the Journal Articles tab."""
    return '<button data-p="journal"><span class="dot" style="background:var(--lit, #1f6f8b)"></span>Journal Articles</button>'


def render_styles() -> str:
    """Return a <style data-journal-css> block for journal section styling.

    Every var(--x) includes a literal fallback so this section renders
    correctly on pages that do not define the variable.
    """
    return """\
<style data-journal-css>
/* ── Journal Articles section ─────────────────────────────────────────── */
.ja-standalone {
  margin-top: 36px;
  padding-top: 24px;
  border-top: 2px solid var(--line, #d9d0bd);
}
.ja-article {
  margin-bottom: 24px;
  padding: 20px 22px 18px;
  background: var(--paper2, #fbf8f1);
  border-radius: 10px;
  box-shadow: var(--shadow, 0 1px 2px rgba(15,61,58,.08), 0 8px 24px rgba(15,61,58,.06));
}
.ja-cite {
  margin: 0 0 10px;
  line-height: 1.45;
  font-size: 0.97em;
}
.ja-meta {
  color: var(--muted, #5d6b62);
  font-size: 0.875em;
  font-family: "JetBrains Mono", monospace;
  letter-spacing: 0.01em;
}
.ja-meta a {
  color: var(--lit, #1f6f8b);
  text-decoration: none;
}
.ja-meta a:hover {
  text-decoration: underline;
}
.ja-abstract {
  border-left: 3px solid var(--lit, #1f6f8b);
  padding: 10px 14px;
  margin: 0 0 18px;
  background: var(--lit-soft, #dcedf2);
  border-radius: 0 6px 6px 0;
  font-size: 0.925em;
  line-height: 1.6;
  color: var(--ink, #0f3d3a);
}
.ja-mcq {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--line, #d9d0bd);
}
.ja-mcq + .ja-mcq {
  margin-top: 10px;
  padding-top: 10px;
}
.ja-q {
  font-weight: 600;
  font-size: 0.93em;
  margin: 0 0 7px;
  color: var(--ink, #0f3d3a);
}
.ja-opts {
  list-style: none;
  margin: 0 0 8px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ja-opt {
  font-size: 0.9em;
  padding: 4px 8px;
  border-radius: 5px;
  color: var(--ink2, #15514c);
  background: transparent;
}
.ja-opt b {
  display: inline-block;
  min-width: 1.5em;
  color: var(--muted, #5d6b62);
  font-family: "JetBrains Mono", monospace;
  font-size: 0.88em;
}
.ja-ans {
  margin-top: 4px;
}
.ja-ans summary {
  display: inline-block;
  cursor: pointer;
  font-size: 0.83em;
  font-family: "JetBrains Mono", monospace;
  padding: 3px 10px;
  border: 1px solid var(--lit, #1f6f8b);
  border-radius: 5px;
  color: var(--lit, #1f6f8b);
  background: transparent;
  user-select: none;
  list-style: none;
}
.ja-ans summary::-webkit-details-marker { display: none; }
.ja-ans summary::marker { display: none; }
.ja-ans summary:hover {
  background: var(--lit-soft, #dcedf2);
}
.ja-ans[open] summary {
  background: var(--lit-soft, #dcedf2);
  margin-bottom: 6px;
}
.ja-ans-body {
  font-size: 0.9em;
  padding: 8px 12px;
  background: var(--paper, #fdfaf4);
  border: 1px solid var(--line, #d9d0bd);
  border-radius: 6px;
  line-height: 1.55;
  color: var(--ink, #0f3d3a);
}
.ja-ans-correct {
  font-weight: 600;
  color: var(--good, #2f7d52);
  display: block;
  margin-bottom: 4px;
}
.ja-ans-rationale {
  color: var(--ink2, #15514c);
}
</style>"""


def render_panel(records: list, standalone: bool = False) -> str:
    """Return a <section> element containing journal article cards.

    If standalone is True, the section uses class "ja-standalone" (visible
    inline) instead of class "panel" (hidden until tab click).
    """

    # Sort by year desc, then title asc
    sorted_records = sorted(records, key=lambda r: (-r["year"], r["title"].lower()))

    articles_html_parts = []
    for rec in sorted_records:
        title = _e(rec["title"])
        year = _e(str(rec["year"]))
        authors = _e(rec["authors"])
        journal = _e(rec["journal"])

        # DOI: render as link if present
        doi_raw = rec.get("doi", "").strip()
        if doi_raw:
            doi_url = doi_raw if doi_raw.startswith("http") else f"https://doi.org/{doi_raw}"
            doi_part = f' &middot; <a href="{_e(doi_url)}" target="_blank" rel="noopener">{_e(doi_raw)}</a>'
        else:
            doi_part = ""

        # Abstract
        abstract_html = _abstract_html(rec["abstract"])

        # MCQs
        mcq_html_parts = []
        for mcq in rec.get("mcqs", []):
            q_text = _e(mcq["q"])
            options = mcq["o"]
            answer_idx = mcq["a"]
            rationale = _e(mcq["e"])
            correct_letter = _LETTERS[answer_idx]
            correct_option = _e(options[answer_idx])

            opts_items = "\n".join(
                f'          <li class="ja-opt"><b>{_LETTERS[i]}.</b> {_e(opt)}</li>'
                for i, opt in enumerate(options)
            )

            mcq_block = f"""\
      <div class="ja-mcq">
        <p class="ja-q">{q_text}</p>
        <ul class="ja-opts">
{opts_items}
        </ul>
        <details class="ja-ans">
          <summary>Show answer</summary>
          <div class="ja-ans-body">
            <span class="ja-ans-correct">Answer: {_e(correct_letter)}. {correct_option}</span>
            <span class="ja-ans-rationale">{rationale}</span>
          </div>
        </details>
      </div>"""
            mcq_html_parts.append(mcq_block)

        mcq_section = "\n" + "\n".join(mcq_html_parts) if mcq_html_parts else ""

        article_block = f"""\
  <div class="card ja-article">
    <p class="ja-cite"><b>{title}</b><br>
    <span class="ja-meta">{authors} &middot; {journal} &middot; {year}{doi_part}</span></p>
    <div class="ja-abstract"><b>Abstract.</b> {abstract_html}</div>{mcq_section}
  </div>"""
        articles_html_parts.append(article_block)

    articles_html = "\n".join(articles_html_parts)

    if standalone:
        section_attrs = 'id="journal" class="ja-standalone"'
    else:
        section_attrs = 'class="panel" id="journal"'

    return f"""\
<section {section_attrs}>
  <h2 class="sec">Additional Resources</h2>
  <p class="lead">Journal Articles (2021–2026). Exam items are drawn from the abstract only — read each abstract, then self-test.</p>
{articles_html}
</section>"""


# ---------------------------------------------------------------------------
# inject()
# ---------------------------------------------------------------------------

def inject(page_path: str) -> bool:
    """
    Inject the Journal Articles section into the given page.

    Two layouts are supported:
      - Tabbed SPA (has id="tabrow"): inject a tab button (JOURNAL-TAB markers)
        AND a hidden panel (<section class="panel" id="journal">) inside
        main>.wrap (JOURNAL-ARTICLES markers).
      - No-tab page (has <main> but no id="tabrow"): inject ONLY a visible
        standalone section (<section id="journal" class="ja-standalone">)
        at the end of <main> content (JOURNAL-ARTICLES markers). No tab button
        is injected.

    page_path is a relative path from the repo root (e.g.
    'physical-health/surgery_anesthesia_hub.html').

    Returns True on success, False if the page was skipped (template mismatch).
    Idempotent: replaces existing marked regions if present.
    """
    abs_path = _REPO_ROOT / page_path
    if not abs_path.exists():
        print(f"  [SKIP] {page_path}: file not found")
        return False

    content = abs_path.read_text(encoding="utf-8")

    # ----------------------------------------------------------------
    # Detect layout
    # ----------------------------------------------------------------
    has_tabrow = bool(re.search(r'id="tabrow"', content))
    has_main = "<main>" in content

    if not has_main:
        print(f"  [SKIP] {page_path}: no <main> element found — not matching expected template")
        return False

    if not has_tabrow and not has_main:
        print(f"  [SKIP] {page_path}: no <main> element found — not matching expected template")
        return False

    # ----------------------------------------------------------------
    # Load records
    # ----------------------------------------------------------------
    all_records = load_catalog(str(_CATALOG_PATH))
    records = [r for r in all_records if r["subdomain_page"] == page_path]
    if not records:
        print(f"  [SKIP] {page_path}: no catalog records for this page")
        return False

    styles_html = render_styles()

    # ----------------------------------------------------------------
    # TABBED layout
    # ----------------------------------------------------------------
    if has_tabrow:
        tab_button_html = render_tab_button()
        panel_html = render_panel(records, standalone=False)

        tab_region = f"{TAB_START}\n{tab_button_html}\n{TAB_END}"
        panel_region = f"{PANEL_START}\n{styles_html}\n{panel_html}\n{PANEL_END}"

        # TAB injection: idempotent replacement or fresh insert
        if TAB_START in content:
            content = re.sub(
                re.escape(TAB_START) + r".*?" + re.escape(TAB_END),
                tab_region,
                content,
                flags=re.DOTALL,
            )
        else:
            tabrow_open_match = re.search(r'<div[^>]+id="tabrow"[^>]*>', content)
            if not tabrow_open_match:
                print(f"  [SKIP] {page_path}: cannot locate #tabrow open tag")
                return False

            search_start = tabrow_open_match.end()
            close_div_match = re.search(r"</div>", content[search_start:])
            if not close_div_match:
                print(f"  [SKIP] {page_path}: cannot find closing </div> for #tabrow")
                return False

            insert_pos = search_start + close_div_match.start()
            content = content[:insert_pos] + "\n" + tab_region + "\n" + content[insert_pos:]

        # PANEL injection: idempotent replacement or fresh insert
        if PANEL_START in content:
            content = re.sub(
                re.escape(PANEL_START) + r".*?" + re.escape(PANEL_END),
                panel_region,
                content,
                flags=re.DOTALL,
            )
        else:
            # Find </div></main> (close of main > .wrap) and insert before it.
            main_close_match = re.search(r"</div>\s*</main>", content)
            if not main_close_match:
                print(f"  [SKIP] {page_path}: cannot locate </div></main> anchor")
                return False

            insert_pos = main_close_match.start()
            content = content[:insert_pos] + "\n" + panel_region + "\n\n" + content[insert_pos:]

    # ----------------------------------------------------------------
    # NO-TAB (standalone) layout
    # ----------------------------------------------------------------
    else:
        panel_html = render_panel(records, standalone=True)
        panel_region = f"{PANEL_START}\n{styles_html}\n{panel_html}\n{PANEL_END}"

        # PANEL injection: idempotent replacement or fresh insert
        if PANEL_START in content:
            content = re.sub(
                re.escape(PANEL_START) + r".*?" + re.escape(PANEL_END),
                panel_region,
                content,
                flags=re.DOTALL,
            )
        else:
            # Insert before </main> (standalone pages may not have </div></main>)
            main_close_match = re.search(r"</main>", content)
            if not main_close_match:
                print(f"  [SKIP] {page_path}: cannot locate </main> anchor")
                return False

            insert_pos = main_close_match.start()
            content = content[:insert_pos] + "\n" + panel_region + "\n\n" + content[insert_pos:]

    # ----------------------------------------------------------------
    # Write back
    # ----------------------------------------------------------------
    abs_path.write_text(content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Inject Journal Articles sections into ABVP hub subdomain pages."
    )
    parser.add_argument(
        "--page",
        metavar="RELPATH",
        help="Only process this relative page path (e.g. physical-health/surgery_anesthesia_hub.html)",
    )
    args = parser.parse_args()

    all_records = load_catalog(str(_CATALOG_PATH))

    # Determine which pages to process
    if args.page:
        pages = [args.page]
    else:
        # All distinct subdomain_pages with ≥1 record
        seen = {}
        for r in all_records:
            sp = r["subdomain_page"]
            seen[sp] = seen.get(sp, 0) + 1
        pages = [p for p, count in seen.items() if count >= 1]

    print(f"Processing {len(pages)} page(s)…\n")
    injected = 0
    skipped = 0
    for page in pages:
        page_records = [r for r in all_records if r["subdomain_page"] == page]
        ok = inject(page)
        if ok:
            print(f"  [OK]   {page} → {len(page_records)} article(s) injected")
            injected += 1
        else:
            skipped += 1

    print(f"\nDone. {injected} page(s) updated, {skipped} page(s) skipped.")


if __name__ == "__main__":
    main()
