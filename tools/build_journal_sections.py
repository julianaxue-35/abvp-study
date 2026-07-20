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
_SYNTH_PATH = _TOOLS_DIR / "synthesized_mcqs.json"

sys.path.insert(0, str(_TOOLS_DIR))
from lib_catalog import load_catalog  # noqa: E402


def load_synth():
    """Load synthesized cross-study MCQs (list of dicts with subdomain_page)."""
    if _SYNTH_PATH.exists():
        return json.loads(_SYNTH_PATH.read_text(encoding="utf-8"))
    return []


def page_questions(page, all_records, synth):
    """All journal questions for a page: per-article mcqs + synthesized ones."""
    qs = []
    for r in all_records:
        if r["subdomain_page"] == page:
            # Optional bank_topic lets an article's MCQs sit under a page's
            # existing topic filter (e.g. "hw" Heartworm) instead of the
            # default "journal" tag. Badge stays "journal" for provenance.
            topic = r.get("bank_topic", "journal")
            for m in r.get("mcqs", []):
                qs.append({"q": m["q"], "o": m["o"], "a": m["a"], "e": m["e"],
                           "t": topic, "f": "journal"})
    for s in synth:
        if s.get("subdomain_page") == page:
            qs.append({"q": s["q"], "o": s["o"], "a": s["a"], "e": s["e"],
                       "t": s.get("bank_topic", "journal"), "f": "journal"})
    return qs


# ---------------------------------------------------------------------------
# Idempotency markers
# ---------------------------------------------------------------------------
TAB_START = "<!-- JOURNAL-TAB:START -->"
TAB_END = "<!-- JOURNAL-TAB:END -->"
PANEL_START = "<!-- JOURNAL-ARTICLES:START -->"
PANEL_END = "<!-- JOURNAL-ARTICLES:END -->"
BANK_START = "<!-- JOURNAL-BANK:START -->"
BANK_END = "<!-- JOURNAL-BANK:END -->"

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


def render_datatab_button() -> str:
    """Tab button for the bespoke .tab/data-tab tab system (research hubs)."""
    return '<button class="tab" data-tab="journal">Journal Articles</button>'


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
/* ── Journal self-test (pages without an MCQ bank) ── */
.ja-quiz { margin-top: 28px; padding-top: 18px; border-top: 1px solid var(--line, #d9d0bd); }
.ja-quiz-h { font-family: "Fraunces", serif; font-weight: 600; font-size: 18px; margin: 0 0 12px; color: var(--ink, #0f3d3a); }
.ja-qcard { background: var(--paper2, #fbf8f1); border: 1px solid var(--line, #d9d0bd); border-radius: 12px; padding: 14px 16px; margin: 12px 0; }
.ja-qstem { font-weight: 600; font-size: 0.95em; margin-bottom: 10px; color: var(--ink, #0f3d3a); }
.ja-qopt { display: block; width: 100%; text-align: left; cursor: pointer; font: inherit; font-size: 0.9em; padding: 8px 11px; margin: 5px 0; border: 1px solid var(--line, #d9d0bd); border-radius: 8px; background: var(--paper, #fdfaf4); color: var(--ink, #0f3d3a); }
.ja-qopt b { color: var(--muted, #5d6b62); font-family: "JetBrains Mono", monospace; margin-right: 4px; }
.ja-qopt:hover:not(.locked) { border-color: var(--lit, #1f6f8b); }
.ja-qopt.locked { cursor: default; }
.ja-qopt.correct { background: #e9f4ee; border-color: var(--good, #2f7d52); }
.ja-qopt.wrong { background: #f8e9e9; border-color: var(--bad, #b23b3b); }
.ja-qexpl { font-size: 0.88em; margin-top: 8px; padding: 9px 12px; background: var(--lit-soft, #dcedf2); border-radius: 8px; color: var(--ink2, #15514c); line-height: 1.5; }
/* ── Journal source badge (self-contained so it renders on any bank page) ── */
.bdg.journal {
  display: inline-block;
  font-family: "JetBrains Mono", monospace;
  font-size: 9.5px;
  letter-spacing: .05em;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: 999px;
  vertical-align: middle;
  white-space: nowrap;
  background: var(--lit-soft, #dcedf2);
  color: var(--lit, #1f6f8b);
}
</style>"""


def render_panel(records: list, standalone: bool = False, quiz_html: str = "") -> str:
    """Return a <section> with abstract-only journal cards (no inline MCQs).

    The self-test questions now live in the page's MCQ Test Bank (or, on
    pages without a bank, in the quiz block appended via quiz_html).

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

        abstract_html = _abstract_html(rec["abstract"])

        article_block = f"""\
  <div class="card ja-article">
    <p class="ja-cite"><b>{title}</b><br>
    <span class="ja-meta">{authors} &middot; {journal} &middot; {year}{doi_part}</span></p>
    <div class="ja-abstract"><b>Abstract.</b> {abstract_html}</div>
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
  <p class="lead">Journal Articles (2021–2026) — exam items are drawn from the abstract only. Read each abstract here; self-test questions are in the MCQ Test Bank.</p>
{articles_html}
{quiz_html}
</section>"""


def render_bank_script(questions: list) -> str:
    """JS block that pushes journal questions into the page's existing Q bank.

    Appended before </body>; relies on the page's classic-script-scope `Q`
    array and `render()` function. Each question carries its own `t` (topic
    filter, default "journal") and `f` (badge, "journal"); a bank_topic in the
    catalog routes an article under a native page filter (e.g. "hw").
    Idempotent via BANK markers.
    """
    payload = json.dumps(questions, ensure_ascii=False)
    return f"""\
<script data-journal-bank>
(function(){{try{{
  // Teach the page's badge/label helpers about journal-sourced questions so
  // they render a "journal" source badge (the page templates predate this tag).
  if(typeof flagBadge==='function' && !flagBadge.__journalPatched){{
    var _fb=flagBadge;
    window.flagBadge=function(f){{return f==='journal'?'<span class="bdg journal">journal</span>':_fb(f);}};
    window.flagBadge.__journalPatched=true;
  }}
  if(typeof tagLabel==='function' && !tagLabel.__journalPatched){{
    var _tl=tagLabel;
    window.tagLabel=function(t){{return t==='journal'?'Journal':_tl(t);}};
    window.tagLabel.__journalPatched=true;
  }}
  // Bespoke #chips banks render each card's tag via DLABEL[item.f]; register a
  // label so journal cards read "Journal Articles" instead of "undefined".
  if(typeof DLABEL==='object' && DLABEL && !DLABEL.journal){{DLABEL.journal='Journal Articles';}}
  // Add a "Journal Articles" chip to whichever topic-filter bar the page uses
  // (.filters on the standard template, #chips on the research hubs) so the
  // journal questions can be isolated (they otherwise sit at the end of bank).
  var _fbar=document.querySelector('.filters')||document.getElementById('chips');
  if(_fbar && !_fbar.querySelector('[data-f="journal"]')){{
    var _jb=document.createElement('button');
    _jb.setAttribute('data-f','journal');
    _jb.textContent='Journal Articles';
    var _sib=_fbar.querySelector('button[data-f]');
    // strip whichever "selected" class the page's own chips use, so the
    // injected chip doesn't render pre-selected ('on' is the standard
    // template, 'active' the research hubs)
    if(_sib && _sib.className){{_jb.className=_sib.className;_jb.classList.remove('active');_jb.classList.remove('on');}}
    _fbar.appendChild(_jb);
  }}
  if(typeof Q!=='undefined' && Array.isArray(Q)){{
    var JJ={payload};
    JJ.forEach(function(m){{Q.push({{t:m.t||"journal",f:m.f||"journal",q:m.q,o:m.o,a:m.a,e:m.e}});}});
    if(typeof render==='function'){{render();}}
  }}
}}catch(e){{}}}})();
</script>"""


def render_quiz_block(questions: list) -> str:
    """Self-contained interactive journal quiz for pages WITHOUT an MCQ bank."""
    payload = json.dumps(questions, ensure_ascii=False)
    return f"""\
  <div class="ja-quiz">
    <h3 class="ja-quiz-h">Journal Self-Test</h3>
    <div id="jaQuizHost"></div>
  </div>
  <script data-journal-quiz>
  (function(){{
    var JQ={payload};
    var host=document.getElementById('jaQuizHost'); if(!host||!JQ.length) return;
    var L=["A","B","C","D"];
    JQ.forEach(function(item,i){{
      var card=document.createElement('div'); card.className='ja-qcard';
      var stem=document.createElement('div'); stem.className='ja-qstem';
      stem.textContent=(i+1)+'. '+item.q; card.appendChild(stem);
      var done=false;
      item.o.forEach(function(opt,oi){{
        var b=document.createElement('button'); b.className='ja-qopt';
        b.innerHTML='<b>'+L[oi]+'.</b> '+opt;
        b.onclick=function(){{
          if(done) return; done=true;
          var kids=card.querySelectorAll('.ja-qopt');
          for(var k=0;k<kids.length;k++){{kids[k].classList.add('locked');}}
          kids[item.a].classList.add('correct');
          if(oi!==item.a) b.classList.add('wrong');
          var ex=document.createElement('div'); ex.className='ja-qexpl';
          ex.innerHTML='<b>Answer: '+L[item.a]+'.</b> '+item.e; card.appendChild(ex);
        }};
        card.appendChild(b);
      }});
      host.appendChild(card);
    }});
  }})();
  </script>"""


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
    # Bespoke tab system used by the research hubs: `.tab` buttons carrying
    # data-tab + `.panel` sections toggled by a .tab click handler (no #tabrow).
    has_datatab = (
        not has_tabrow
        and bool(re.search(r'<button class="tab[^"]*"\s+data-tab="', content))
        and 'class="panel' in content
    )

    if not has_main:
        print(f"  [SKIP] {page_path}: no <main> element found — not matching expected template")
        return False

    if not has_tabrow and not has_main:
        print(f"  [SKIP] {page_path}: no <main> element found — not matching expected template")
        return False

    # ----------------------------------------------------------------
    # Load records + questions
    # ----------------------------------------------------------------
    all_records = load_catalog(str(_CATALOG_PATH))
    synth = load_synth()
    records = [r for r in all_records if r["subdomain_page"] == page_path]
    if not records:
        print(f"  [SKIP] {page_path}: no catalog records for this page")
        return False

    questions = page_questions(page_path, all_records, synth)
    has_bank = bool(re.search(r"const Q=\[", content))
    # Route questions into the page's MCQ bank only when its filter bar uses
    # event delegation — either on .filters (standard template) or on #chips
    # (the bespoke research-domain hubs). That is the only case where a
    # dynamically injected "Journal Articles" chip gets wired up. Pages that
    # bind filter clicks per-button at load (a dynamic chip would be dead) or
    # that have no filter bar get a self-contained in-panel "Journal Self-Test".
    has_delegated_filter = has_bank and bool(
        re.search(
            r"""(?:querySelector\(["']\.filters["']\)|getElementById\(["']chips["']\))"""
            r"""\.addEventListener\(["']click""",
            content,
        )
    )
    # Never downgrade a page that is already on the merged-bank style. The
    # heuristic above misfires on some pages (06_mental_health.html among
    # them), and falling back to the standalone quiz there is a silent
    # regression: the questions leave the main Q array, so they lose both the
    # "Journal Articles" filter chip and the site-wide Fisher-Yates answer
    # shuffle, which only patches Q. All 39 pages carrying journal questions
    # use the merged-bank style; none use the standalone quiz.
    already_bank = "data-journal-bank" in content
    if already_bank and not has_delegated_filter:
        print(
            "         note: keeping existing merged-bank style "
            "(filter heuristic would have downgraded this page)"
        )
    use_bank = has_delegated_filter or already_bank
    quiz_html = "" if use_bank else render_quiz_block(questions)

    styles_html = render_styles()

    # ----------------------------------------------------------------
    # TABBED layout
    # ----------------------------------------------------------------
    if has_tabrow:
        tab_button_html = render_tab_button()
        panel_html = render_panel(records, standalone=False, quiz_html=quiz_html)

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
    # BESPOKE TAB layout (.tab/data-tab — research hubs)
    # ----------------------------------------------------------------
    elif has_datatab:
        tab_button_html = render_datatab_button()
        panel_html = render_panel(records, standalone=False, quiz_html=quiz_html)

        tab_region = f"{TAB_START}\n{tab_button_html}\n{TAB_END}"
        panel_region = f"{PANEL_START}\n{styles_html}\n{panel_html}\n{PANEL_END}"

        # TAB injection: idempotent replacement, else insert after the last
        # existing .tab button (e.g. "Question Bank") in the tab nav.
        if TAB_START in content:
            content = re.sub(
                re.escape(TAB_START) + r".*?" + re.escape(TAB_END),
                tab_region,
                content,
                flags=re.DOTALL,
            )
        else:
            tab_btns = list(
                re.finditer(
                    r'<button class="tab[^"]*"\s+data-tab="[^"]*"[^>]*>.*?</button>',
                    content,
                    flags=re.DOTALL,
                )
            )
            if not tab_btns:
                print(f"  [SKIP] {page_path}: cannot locate .tab/data-tab buttons")
                return False
            insert_pos = tab_btns[-1].end()
            content = content[:insert_pos] + "\n    " + tab_region + content[insert_pos:]

        # PANEL injection: idempotent replacement, else insert before </main>.
        # standalone=False renders <section class="panel" id="journal"> so the
        # page's existing .tab handler shows/hides it like every other panel.
        if PANEL_START in content:
            content = re.sub(
                re.escape(PANEL_START) + r".*?" + re.escape(PANEL_END),
                panel_region,
                content,
                flags=re.DOTALL,
            )
        else:
            main_close_match = re.search(r"</main>", content)
            if not main_close_match:
                print(f"  [SKIP] {page_path}: cannot locate </main> anchor")
                return False
            insert_pos = main_close_match.start()
            content = content[:insert_pos] + "\n" + panel_region + "\n\n" + content[insert_pos:]

    # ----------------------------------------------------------------
    # NO-TAB (standalone) layout
    # ----------------------------------------------------------------
    else:
        panel_html = render_panel(records, standalone=True, quiz_html=quiz_html)
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
    # Bank push script (pages with a `const Q=[` MCQ Test Bank)
    # ----------------------------------------------------------------
    # Remove any existing bank block first (idempotent / handles transitions).
    content = re.sub(
        re.escape(BANK_START) + r".*?" + re.escape(BANK_END) + r"\n?",
        "",
        content,
        flags=re.DOTALL,
    )
    if use_bank and questions:
        bank_region = f"{BANK_START}\n{render_bank_script(questions)}\n{BANK_END}"
        body_close = content.rfind("</body>")
        if body_close != -1:
            content = content[:body_close] + bank_region + "\n" + content[body_close:]
        else:
            print(f"  [WARN] {page_path}: no </body> for bank script")

    # ----------------------------------------------------------------
    # Write back
    # ----------------------------------------------------------------
    abs_path.write_text(content, encoding="utf-8")

    # Re-apply the per-question answer shuffle. The generated bank is emitted
    # unshuffled, and the journal questions are pushed into Q *after* the
    # page's own /*mcq-shuffle*/ block has already run — so without this the
    # journal answers stay in their original, heavily clustered order even
    # though the page looks shuffled.
    try:
        from add_mcq_shuffle import inject_file
        injected = inject_file(str(abs_path))
        if injected:
            print(f"         re-applied answer shuffle ({'+'.join(injected)})")
    except Exception as exc:
        print(f"  [WARN] {page_path}: could not re-apply answer shuffle: {exc}")
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
