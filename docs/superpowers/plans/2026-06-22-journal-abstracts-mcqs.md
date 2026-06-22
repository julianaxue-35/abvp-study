# Journal Abstracts + MCQs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a catalog-driven "Additional Resources → Journal Articles" section (citation + real abstract + 2–3 abstract-only MCQs) to every relevant ABVP hub subdomain page, sourced from Juliana's `journal article` folder plus best-effort gap discovery (2021–2026).

**Architecture:** A `tools/journal-catalog.json` is the single source of truth. Python scripts extract abstracts from folder PDFs, map each article to a subdomain page, attach MCQs, and a generator injects an idempotent HTML block (delimited by markers) into each page. Pilot one page, get sign-off, then roll out.

**Tech Stack:** Python 3 (stdlib only), `pdftotext` (poppler, already installed at /opt/homebrew/bin), WebSearch/WebFetch for discovery, vanilla JS/CSS in the HTML pages.

## Global Constraints

- Look-back window: **2021, 2022, 2023, 2024, 2025, 2026** only. Drop anything outside.
- **Abstract only.** MCQs must be answerable from the abstract text alone. No full-text or outside facts.
- **No fabrication.** Abstract text is extracted from the PDF or fetched from a real free source. If no genuine free abstract exists, drop the article and log it.
- Each MCQ: single-best-answer, 4 options, `a` = 0-based index of correct option, `e` = abstract-grounded rationale.
- Injected HTML block is bounded by `<!-- JOURNAL-ARTICLES:START -->` / `<!-- JOURNAL-ARTICLES:END -->` and must be idempotent (re-run replaces, never duplicates).
- Match each page's existing CSS variables/classes; do not load external libraries.
- Folder path: `/Users/jxue/Library/CloudStorage/Dropbox/work docs/ABVP specialist pathway/reading list/journal article/`
- Repo: `/Users/jxue/abvp-study/` (commit + `git push` deploys via GitHub Pages).

---

### Task 1: Tooling scaffold + catalog schema

**Files:**
- Create: `tools/journal_catalog_schema.md` (human-readable record shape)
- Create: `tools/lib_catalog.py` (load/save/validate catalog)
- Create: `tools/journal-catalog.json` (empty `[]` to start)

**Interfaces:**
- Produces: `load_catalog(path) -> list[dict]`, `save_catalog(path, records) -> None`, `validate_record(rec) -> list[str]` (returns list of problems, empty = valid). Record keys per spec: `id,title,authors,journal,year,citation,doi,source,abstract,abstract_origin,domain,subdomain_page,mcqs`.

- [ ] **Step 1:** Write `tools/lib_catalog.py` with `load_catalog`, `save_catalog`, and `validate_record` (checks: required keys present, `year` in 2021–2026, `source` in {folder,discovered}, `subdomain_page` is a path that exists under repo, each mcq has `q/o/a/e` with `len(o)==4` and `0<=a<4`).
- [ ] **Step 2:** Write `tools/journal-catalog.json` containing `[]`.
- [ ] **Step 3:** Run `python3 -c "import tools.lib_catalog as c; print(c.load_catalog('tools/journal-catalog.json'))"` — Expected: `[]`.
- [ ] **Step 4:** Commit (`tools: catalog schema + load/save/validate helpers`).

---

### Task 2: Extract abstracts + metadata from folder PDFs

**Files:**
- Create: `tools/extract_folder.py`
- Modify: `tools/journal-catalog.json` (populated with `source:"folder"` records)
- Create: `tools/extract_report.md` (per-file: abstract found? mapped subdomain?)

**Interfaces:**
- Consumes: `lib_catalog`.
- Produces: catalog entries for every folder PDF where an abstract is extractable. `extract_abstract(text) -> str|None`, `guess_subdomain(title, text) -> (domain, page)` using a keyword→page rule table.

- [ ] **Step 1:** Write `tools/extract_folder.py` that, for each PDF in the folder: runs `pdftotext -layout`, extracts citation (title from filename minus `[Abstract]`/`.pdf`, plus any author/journal/year found in text), extracts the abstract (heuristics: text after "Abstract"/"Summary" heading up to "Introduction"/"Keywords"; for JSMCAH `[Abstract]` PDFs grab the abstract body), and maps to a subdomain via `guess_subdomain`.
- [ ] **Step 2:** Build the keyword→page rule table covering all subdomain pages (e.g. castrat|spay|neuter|anesth|surg → surgery_anesthesia; parvo|panleuk|URI|distemper|outbreak → infectious_disease; TNR|community cat|free-roaming → companion-animal-homelessness/... etc.). Default-to-review bucket for ambiguous ones.
- [ ] **Step 3:** Run `python3 tools/extract_folder.py` — writes catalog + `extract_report.md`.
- [ ] **Step 4:** Verify: `python3 -c "import json;d=json.load(open('tools/journal-catalog.json'));print(len(d),'records');print(sum(1 for r in d if not r['abstract']),'missing abstracts')"`. Manually skim `extract_report.md` for mis-maps; fix rule table and re-run.
- [ ] **Step 5:** Commit (`tools: extract folder abstracts into catalog`).

---

### Task 3: MCQ generator (Surgery & Anesthesia subset) — PILOT content

**Files:**
- Modify: `tools/journal-catalog.json` (add `mcqs` to surgery/anesthesia records)

**Interfaces:**
- Consumes: catalog records where `subdomain_page` endswith `surgery_anesthesia_hub.html`.

- [ ] **Step 1:** For each surgery/anesthesia article, write 2–3 single-best-answer MCQs grounded only in its abstract (test the article's actual finding/method/conclusion). Add to that record's `mcqs`.
- [ ] **Step 2:** Verify each MCQ: re-read the abstract, confirm the keyed answer is supported by the abstract and distractors are clearly wrong. Confirm `validate_record` passes for every surgery record.
- [ ] **Step 3:** Commit (`content: MCQs for surgery/anesthesia journal articles`).

---

### Task 4: Section generator + PILOT injection (Surgery & Anesthesia)

**Files:**
- Create: `tools/build_journal_sections.py`
- Modify: `physical-health/surgery_anesthesia_hub.html`

**Interfaces:**
- Consumes: catalog, `lib_catalog`.
- Produces: `render_block(records_for_page) -> html_str`; `inject(page_path, html_str)` that replaces content between the START/END markers, inserting them (before the closing main/quiz script area) if absent.

- [ ] **Step 1:** Write `render_block`: an "Additional Resources" heading + "Journal Articles (2021–2026)" subheading, then one card per article (citation, abstract, each MCQ with options + a **Show answer** `<details>`/button toggle revealing correct option + rationale). Use the page's existing CSS classes; add minimal scoped CSS only if needed.
- [ ] **Step 2:** Write `inject` with idempotent START/END markers. Add `--page` filter so it can target one page.
- [ ] **Step 3:** Run `python3 tools/build_journal_sections.py --page physical-health/surgery_anesthesia_hub.html`.
- [ ] **Step 4:** Verify: open the file, confirm one block, valid HTML (`python3 -c "import html.parser..."` smoke check or `node --check` not applicable; do a tag-balance grep), toggles present. Re-run the command and confirm still exactly one block (idempotent).
- [ ] **Step 5:** Commit (`feat: journal articles section — surgery/anesthesia pilot`). **PILOT SIGN-OFF GATE: show Juliana the rendered page before proceeding.**

---

### Task 5: Gap discovery — JSMCAH (complete) + other journals (targeted)

**Files:**
- Modify: `tools/journal-catalog.json` (add `source:"discovered"` records)
- Create: `tools/discovery_log.md` (searched / found / skipped-no-free-abstract)

**Interfaces:**
- Consumes: catalog (to diff against existing titles).
- Produces: new catalog records with real fetched abstracts.

- [ ] **Step 1:** Enumerate JSMCAH 2021–2026 (journal site / PubMed). For each shelter-relevant article not already in catalog, fetch the real free abstract; add record. Log everything.
- [ ] **Step 2:** Run targeted WebSearches for shelter-medicine-relevant 2021–2026 articles in the other 22 journals (query per high-yield topic × journal). Add only those with a confirmed free abstract; log skips.
- [ ] **Step 3:** Map each new record to a subdomain page (reuse `guess_subdomain`). Generate 2–3 abstract-only MCQs per new record.
- [ ] **Step 4:** Verify: `validate_record` passes for all; spot-check 5 discovered abstracts against their source URLs for fidelity.
- [ ] **Step 5:** Commit (`content: gap-discovered journal articles + MCQs`).

---

### Task 6: MCQs for all remaining folder articles

**Files:**
- Modify: `tools/journal-catalog.json`

- [ ] **Step 1:** For every catalog record still lacking `mcqs` (non-surgery folder articles), write 2–3 abstract-only MCQs.
- [ ] **Step 2:** Verify `validate_record` passes for the whole catalog; confirm zero records have empty `mcqs` (except logged drops).
- [ ] **Step 3:** Commit (`content: MCQs for remaining folder articles`).

---

### Task 7: Full rollout — inject all pages

**Files:**
- Modify: all subdomain `*.html` pages that have ≥1 mapped article.

- [ ] **Step 1:** Run `python3 tools/build_journal_sections.py` (no `--page` = all pages). Generator groups catalog by `subdomain_page` and injects each.
- [ ] **Step 2:** Verify: for each modified page, exactly one START/END block; tag-balance grep clean; article counts match catalog grouping. Re-run to confirm idempotency.
- [ ] **Step 3:** Spot-check 3 pages in browser/preview for rendering + toggles.
- [ ] **Step 4:** Commit (`feat: journal articles sections across all hub pages`).

---

### Task 8: Ship + summary

**Files:**
- Create: `tools/coverage_summary.md` (articles per domain/page, total MCQs, discovery gaps/caveats)

- [ ] **Step 1:** Generate `coverage_summary.md` from the catalog.
- [ ] **Step 2:** `git push`; confirm Pages deploy (wait ~1 min, curl a page for the marker).
- [ ] **Step 3:** Report to Juliana: counts, the discovery coverage caveat, any dropped articles.
- [ ] **Step 4:** Commit any summary docs (`docs: journal coverage summary`).
