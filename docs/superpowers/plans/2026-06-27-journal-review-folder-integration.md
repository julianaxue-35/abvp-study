# Journal Review Folder → Hub Integration + 2025–2026 Discovery — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fold ~645 new 2021–2024 journal articles from Juliana's board-review spreadsheets into the ABVP hub (abstract + 2–3 MCQs each, via the existing catalog pipeline), and produce a diplomate-comprehensive 2025–2026 article review spreadsheet whose approved entries are then added to the hub.

**Architecture:** Deterministic Python does extraction/dedup/spreadsheet-building; a multi-agent Workflow does domain-assignment + MCQ-writing + adversarial verification. Workflow agents read their input slice from disk and write validated output as numbered partial JSON files (Workflow scripts have no filesystem access); Python merges the partials and runs the existing `build_journal_sections.py` / `build_mock_journal.py`. Two human review gates: the folder duplicate report, and the 2025–26 spreadsheet.

**Tech Stack:** Python 3.9 (`openpyxl`, `python-docx`, stdlib `difflib`/`json`/`re`), the repo's `tools/lib_catalog.py` + build scripts, the Workflow tool (multi-agent), `pytest` for the deterministic scripts.

## Global Constraints

- **Repo (canonical/live):** `/Users/jxue/abvp-study`. Dropbox HTML copies are stale — never copy Dropbox→repo blindly.
- **Source folder:** `/Users/jxue/Library/CloudStorage/Dropbox/work docs/protocols in interactive dashboards/ABVP exam hub/2026 ABVP shelter medicine study/JOURNAL REVIEW`
- **Single source of truth:** `tools/journal-catalog.json`. Never hand-edit subdomain HTML; regenerate via build scripts.
- **Record schema** (enforced by `lib_catalog.validate_record`): keys `id, title, authors, journal, year, citation, doi, source, abstract, abstract_origin, domain, subdomain_page, mcqs`. `year` int in **2021–2026**. `source` ∈ {`folder`,`discovered`}. `subdomain_page` must resolve to an existing file under repo root. `abstract` non-empty. Each MCQ = `{q, o(exactly 4), a(int 0–3), e}`, `q`/`e` non-empty.
- **Folder articles:** `source="folder"`, `abstract_origin="spreadsheet"`. **Discovered articles:** `source="discovered"`, `abstract_origin="pubmed"` (or `"web"`).
- **MCQs:** 2–3 per article, closed-book, conclusion-focused, answerable from the abstract alone.
- **Year scope:** folder = 2021–2024; discovery = 2025–2026.
- **Scratchpad** for throwaway files: `/private/tmp/claude-501/-Users-jxue/259cb740-6813-4508-b73f-6e7e53932b02/scratchpad`. Durable artifacts live under `tools/`.
- **PATH:** prepend `/opt/homebrew/bin` in every Bash step.
- **Commits:** only when a step says to. Per-domain commits during deploy.

---

## File Structure

**Create:**
- `tools/extract_folder_articles.py` — deterministic extraction + dedup → `folder_new_articles.json` + dedup report.
- `tools/lib_extract.py` — pure helper functions (column detection, normalization, year detection, fuzzy dedup) — unit-tested.
- `tools/build_review_spreadsheet.py` — builds the 4-tab 2025–26 `.xlsx` from discovery partials.
- `tools/merge_partials.py` — merges numbered partial JSON files → one validated record list.
- `tools/workflows/folder_mcqs.workflow.js` — Workflow script: domain-assign + MCQ-write + verify for folder articles.
- `tools/workflows/discovery_2025_2026.workflow.js` — Workflow script: diplomate + topic discovery.
- `tools/tests/test_lib_extract.py` — pytest unit tests for `lib_extract`.
- `tools/tests/fixtures/` — tiny synthetic `.xlsx` + catalog slice for tests.
- `tools/folder_new_articles.json` (generated) — staged worklist.
- `tools/folder_dedup_report.md` + `tools/folder_dedup_report.xlsx` (generated) — review gate.
- `tools/qa_fixes/folder_batch_*.json` (generated) — workflow output partials.
- `tools/discovery_2025_2026/diplomate_roster.json` (generated) — roster.
- `tools/discovery_2025_2026/cand_*.json` (generated) — discovery partials.
- `2025-2026-shelter-med-articles.xlsx` (generated, repo root) — the review deliverable.

**Modify:**
- `tools/journal-catalog.json` — append validated records (Tasks 4, 9).
- `~/.claude/projects/-Users-jxue/memory/project_journal_abstracts_hub.md` + `MEMORY.md` (Task 10).

**Reuse unchanged:** `tools/lib_catalog.py`, `tools/build_journal_sections.py`, `tools/build_mock_journal.py`.

---

## Task 1: `lib_extract` helpers (column detection, normalization, dedup)

**Files:**
- Create: `tools/lib_extract.py`
- Test: `tools/tests/test_lib_extract.py`

**Interfaces:**
- Produces:
  - `norm_title(s: str) -> str` — lowercase, alphanumerics only.
  - `detect_year(row: list, header_map: dict) -> int|None` — year from a Year column or scanned from any cell.
  - `find_cols(headers: list[str]) -> dict` — maps logical names → column indices: keys `title, abstract, author, journal, year, keypoints, diplomate`. Handles a combined `"First Author, Journal"` header (sets both `author` and a `combined_author_journal` flag).
  - `is_dup(norm: str, author_last: str, year: int, existing: dict) -> bool` — exact dup test against an index built from the catalog.
  - `fuzzy_matches(norm: str, existing_norms: list[str], lo=0.80, hi=0.99) -> list[tuple[str,float]]` — near-dups via `difflib.SequenceMatcher`.

- [ ] **Step 1: Write failing tests**

```python
# tools/tests/test_lib_extract.py
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib_extract import norm_title, find_cols, detect_year, fuzzy_matches

def test_norm_title_strips_nonalnum_and_lowercases():
    assert norm_title("Tag! You’re Home!  ") == "tagyourehome"

def test_find_cols_standard_infectious_layout():
    cols = find_cols(["Year","First Author","Journal","Article Title","Abstract","Key Points"])
    assert cols["year"] == 0 and cols["author"] == 1 and cols["journal"] == 2
    assert cols["title"] == 3 and cols["abstract"] == 4 and cols["keypoints"] == 5

def test_find_cols_combined_author_journal():
    cols = find_cols([" ","First Author, Journal","Article Title","Abstract"])
    assert cols["author"] == 1 and cols.get("combined_author_journal") is True
    assert cols["title"] == 2 and cols["abstract"] == 3

def test_find_cols_diplomate_layout():
    cols = find_cols(["Diplomate","Journal","Year","Author","Title","Abstract"])
    assert cols["diplomate"] == 0 and cols["journal"] == 1 and cols["year"] == 2
    assert cols["author"] == 3 and cols["title"] == 4 and cols["abstract"] == 5

def test_detect_year_from_year_column():
    assert detect_year([2024.0,"x"], {"year":0}) == 2024

def test_detect_year_scanned_from_text():
    assert detect_year(["2020/2021","Animals"], {}) == 2020

def test_fuzzy_matches_flags_near_dup():
    got = fuzzy_matches("tagyourehomereunificationofpetcats",
                        ["tagyourehomereunificationofpetcat"], 0.80, 0.99)
    assert got and got[0][1] >= 0.80
```

- [ ] **Step 2: Run, verify fail**

Run: `export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && python3 -m pytest tools/tests/test_lib_extract.py -q`
Expected: FAIL (`ModuleNotFoundError: lib_extract`).

- [ ] **Step 3: Implement `tools/lib_extract.py`**

```python
"""lib_extract.py — pure helpers for folder-article extraction & dedup."""
import re
from difflib import SequenceMatcher

def norm_title(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

def find_cols(headers: list) -> dict:
    h = [str(c).strip().lower() if c is not None else "" for c in headers]
    cols = {}
    for i, name in enumerate(h):
        if not name:
            continue
        if "author" in name and "journal" in name:
            cols.setdefault("author", i); cols["combined_author_journal"] = True
            continue
        if "title" in name:        cols.setdefault("title", i)
        elif "abstract" in name:   cols.setdefault("abstract", i)
        elif "diplomate" in name:  cols.setdefault("diplomate", i)
        elif "author" in name:     cols.setdefault("author", i)
        elif "journal" in name and "year" not in name: cols.setdefault("journal", i)
        elif name == "year" or "article year" in name: cols.setdefault("year", i)
        elif "key" in name and ("point" in name or "takeaway" in name): cols.setdefault("keypoints", i)
        elif "takeaway" in name:   cols.setdefault("keypoints", i)
    return cols

def detect_year(row: list, header_map: dict):
    yc = header_map.get("year")
    if yc is not None and yc < len(row) and row[yc] is not None:
        v = row[yc]
        if isinstance(v, (int, float)) and 1990 < v < 2030:
            return int(v)
        m = re.search(r"\b(20[0-2]\d)\b", str(v))
        if m: return int(m.group(1))
    for c in row:
        if isinstance(c, (int, float)) and 1990 < c < 2030:
            return int(c)
    for c in row:
        if isinstance(c, str):
            m = re.search(r"\b(20[0-2]\d)\b", c)
            if m: return int(m.group(1))
    return None

def author_lastname(authors: str) -> str:
    a = str(authors).strip()
    if not a: return ""
    first = re.split(r"[,;&]", a)[0].strip()
    return re.sub(r"[^a-z]", "", first.split()[-1].lower()) if first else ""

def is_dup(norm: str, author_last: str, year, existing: dict) -> bool:
    if norm in existing["titles"]:
        return True
    return (author_last, year) in existing["author_year"] and len(norm) > 12 and any(
        SequenceMatcher(None, norm, e).ratio() >= 0.90 for e in existing["by_ay"].get((author_last, year), [])
    )

def fuzzy_matches(norm: str, existing_norms: list, lo=0.80, hi=0.99) -> list:
    out = []
    for e in existing_norms:
        r = SequenceMatcher(None, norm, e).ratio()
        if lo <= r < hi:
            out.append((e, round(r, 3)))
    return sorted(out, key=lambda x: -x[1])
```

- [ ] **Step 4: Run, verify pass**

Run: `export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && python3 -m pytest tools/tests/test_lib_extract.py -q`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit**

```bash
cd ~/abvp-study && git add tools/lib_extract.py tools/tests/test_lib_extract.py && git commit -m "feat(journal): add lib_extract helpers for folder extraction + dedup"
```

---

## Task 2: Extraction & dedup script → worklist + dedup report

**Files:**
- Create: `tools/extract_folder_articles.py`
- Consumes: `lib_extract` (Task 1), `lib_catalog.load_catalog`.
- Produces: `tools/folder_new_articles.json`, `tools/folder_dedup_report.md`, `tools/folder_dedup_report.xlsx`.

**Interfaces:**
- Each staged record: `{title, authors, journal, year, abstract, key_points, source_sheet, suggested_domain, suggested_page, source:"folder", abstract_origin:"spreadsheet", mcqs:[]}`.

- [ ] **Step 1: Write `tools/extract_folder_articles.py`**

```python
#!/usr/bin/env python3
"""Extract new 2021-2024 folder articles, dedup vs catalog, emit worklist + report."""
import json, sys
from pathlib import Path
import openpyxl
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from lib_extract import norm_title, find_cols, detect_year, author_lastname, is_dup, fuzzy_matches
from lib_catalog import load_catalog

SS = Path("/Users/jxue/Library/CloudStorage/Dropbox/work docs/protocols in interactive dashboards/ABVP exam hub/2026 ABVP shelter medicine study/JOURNAL REVIEW/SPREADSHEETS")
ACTIVE = ["2025 Diplomate publications spreadsheet.xlsx",
          "_Behaviour and Welfare Articles Board Review 2024.xlsx",
          "_Infectious Disease articles - 2024.xlsx",
          "_Misc Spreadsheet Study Guide - Boards 2024.xlsx"]

# sheet name (lower) -> (domain, subdomain_page). Stage-0 seed; the agent refines.
SHEET_MAP = {
  "cirdc":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "dermatophytosis":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "cpv":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "fpv":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "fiv.felv":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "feline uri":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "sars-cov-2":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "fip.fecov":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "other":("Physical Health of Animal","physical-health/infectious_disease_hub.html"),
  "heartworm":("Physical Health of Animal","physical-health/parasites_hub.html"),
  "parasitology":("Physical Health of Animal","physical-health/parasites_hub.html"),
  "anesthesiaanalgesia":("Physical Health of Animal","physical-health/surgery_anesthesia_hub.html"),
  "spayneuter surgery":("Companion Animal Homelessness","companion-animal-homelessness/spay_neuter_hub_2.html"),
  "agebenefits of spayneuter":("Companion Animal Homelessness","companion-animal-homelessness/spay_neuter_hub_2.html"),
  "snrtnr":("Companion Animal Homelessness","companion-animal-homelessness/nonsurgical_sterilization_hub.html"),
  "outreach for owned animals":("Companion Animal Homelessness","companion-animal-homelessness/access_vet_care_hub.html"),
  "transport":("Companion Animal Homelessness","companion-animal-homelessness/animal_transport_relocation_hub.html"),
  "disaster":("Companion Animal Homelessness","companion-animal-homelessness/disaster_emergency_hub.html"),
  "mgmt stats design sanitation":("Shelter Management","shelter-management/05_data_analysis.html"),
  "mental health":("Shelter Management","shelter-management/06_mental_health.html"),
  "forensicscrueltyhoarding":("Community and Public Health","community-public-health/01_animal_cruelty.html"),
  "public health  one health  zoon":("Community and Public Health","community-public-health/02_zoonotic_disease.html"),
  "k9 behaviour & training":("Behavioral Health","behavioral-health/14_training_bmod_playgroups.html"),
  "k9 behaviour assessments":("Behavioral Health","behavioral-health/03_assessment_decision_making.html"),
  "fel behaviour & training":("Behavioral Health","behavioral-health/14_training_bmod_playgroups.html"),
  "psychopharm & pheromones":("Behavioral Health","behavioral-health/09_behaviour_medications.html"),
  "welfarehousingc4c":("Behavioral Health","behavioral-health/07_facility_environment.html"),
  "intakeoutcomelos":("Shelter Management","shelter-management/05_data_analysis.html"),
  "pediatrics":("Physical Health of Animal","physical-health/medical_health_hub.html"),
  "small mammal, exotic, farm":("Physical Health of Animal","physical-health/other-animals_hub.html"),
  "general medicine":("Physical Health of Animal","physical-health/medical_health_hub.html"),
  "misc":("Shelter Management","shelter-management/03_management_leadership.html"),
  "diplomate publications":("Companion Animal Homelessness","companion-animal-homelessness/access_vet_care_hub.html"),
  "abvp journal club articles":("Companion Animal Homelessness","companion-animal-homelessness/access_vet_care_hub.html"),
}
DEFAULT_MAP = ("Shelter Management","shelter-management/03_management_leadership.html")

def build_existing_index(catalog):
    idx = {"titles": set(), "author_year": set(), "by_ay": {}}
    for r in catalog:
        n = norm_title(r["title"]); idx["titles"].add(n)
        al = author_lastname(r.get("authors","")); yr = r.get("year")
        idx["author_year"].add((al, yr)); idx["by_ay"].setdefault((al, yr), []).append(n)
    return idx

def main():
    catalog = load_catalog(str(TOOLS/"journal-catalog.json"))
    existing = build_existing_index(catalog)
    existing_norms = list(existing["titles"])
    staged, dropped, nearlist, seen = [], [], [], set()
    for fname in ACTIVE:
        wb = openpyxl.load_workbook(SS/fname, read_only=True, data_only=True)
        for sn in wb.sheetnames:
            ws = wb[sn]; rows = list(ws.iter_rows(values_only=True))
            if not rows: continue
            cols = find_cols(rows[0])
            if "title" not in cols or "abstract" not in cols: continue
            dom, page = SHEET_MAP.get(sn.strip().lower(), DEFAULT_MAP)
            for r in rows[1:]:
                tc = cols["title"]
                if tc >= len(r) or not r[tc] or not str(r[tc]).strip(): continue
                title = str(r[tc]).strip()
                year = detect_year(list(r), cols)
                if not year or not (2021 <= year <= 2024): continue
                ab = r[cols["abstract"]] if cols["abstract"] < len(r) else None
                abstract = str(ab).strip() if ab else ""
                if len(abstract) < 40: continue  # need a real abstract to write MCQs
                authors = str(r[cols["author"]]).strip() if cols.get("author") is not None and cols["author"] < len(r) and r[cols["author"]] else ""
                journal = str(r[cols["journal"]]).strip() if cols.get("journal") is not None and cols["journal"] < len(r) and r[cols["journal"]] else ""
                if cols.get("combined_author_journal"): journal = ""  # author col holds both; agent refines
                kp = str(r[cols["keypoints"]]).strip() if cols.get("keypoints") is not None and cols["keypoints"] < len(r) and r[cols["keypoints"]] else ""
                n = norm_title(title)
                if n in seen: continue
                al = author_lastname(authors)
                if is_dup(n, al, year, existing):
                    dropped.append({"title": title, "year": year, "sheet": sn}); continue
                fm = fuzzy_matches(n, existing_norms)
                if fm:
                    nearlist.append({"title": title, "year": year, "sheet": sn, "best": fm[0][0], "score": fm[0][1]})
                seen.add(n)
                staged.append({"title": title, "authors": authors, "journal": journal, "year": year,
                               "abstract": abstract, "key_points": kp, "source_sheet": sn,
                               "suggested_domain": dom, "suggested_page": page,
                               "source": "folder", "abstract_origin": "spreadsheet", "mcqs": []})
        wb.close()
    (TOOLS/"folder_new_articles.json").write_text(json.dumps(staged, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    # report
    from collections import Counter
    by_year = Counter(s["year"] for s in staged); by_dom = Counter(s["suggested_domain"] for s in staged)
    lines = [f"# Folder dedup report\n", f"- Staged NEW articles: **{len(staged)}**",
             f"- Exact duplicates dropped: {len(dropped)}", f"- Near-duplicates to eyeball: {len(nearlist)}\n",
             f"## By year\n" + "\n".join(f"- {k}: {v}" for k,v in sorted(by_year.items())),
             f"\n## By suggested domain\n" + "\n".join(f"- {k}: {v}" for k,v in sorted(by_dom.items())),
             f"\n## Near-duplicates (review these)\n" + ("\n".join(f"- [{x['score']}] {x['year']} {x['title'][:80]}  ⟷  {x['best'][:50]}" for x in nearlist) or "_none_")]
    (TOOLS/"folder_dedup_report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    # xlsx report
    out = openpyxl.Workbook(); ws = out.active; ws.title = "Near-dups"
    ws.append(["Score","Year","Title","Sheet","Closest existing (normalized)"])
    for x in nearlist: ws.append([x["score"], x["year"], x["title"], x["sheet"], x["best"]])
    ws2 = out.create_sheet("Dropped exact dups"); ws2.append(["Year","Title","Sheet"])
    for x in dropped: ws2.append([x["year"], x["title"], x["sheet"]])
    out.save(TOOLS/"folder_dedup_report.xlsx")
    print(f"staged={len(staged)} dropped={len(dropped)} near={len(nearlist)}")
    print("by_year:", dict(sorted(by_year.items())))

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run it**

Run: `export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && python3 tools/extract_folder_articles.py`
Expected: prints `staged=` ~600–650, `by_year` showing 2021–2024 only, no 2025/2026.

- [ ] **Step 3: Verify output integrity**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
python3 -c "import json;d=json.load(open('tools/folder_new_articles.json'));print('records',len(d));print('all 21-24',all(2021<=r['year']<=2024 for r in d));print('all have abstract',all(len(r['abstract'])>=40 for r in d));print('pages valid',all(__import__('pathlib').Path(r['suggested_page']).exists() for r in d))"
```
Expected: `records ~600-650`, `all 21-24 True`, `all have abstract True`, `pages valid True`.

- [ ] **Step 4: Commit**

```bash
cd ~/abvp-study && git add tools/extract_folder_articles.py tools/folder_new_articles.json tools/folder_dedup_report.md tools/folder_dedup_report.xlsx && git commit -m "feat(journal): extract + dedup new 2021-2024 folder articles into worklist"
```

---

## Task 3: REVIEW GATE — folder duplicate report (human checkpoint)

**Files:** none (presentation).

- [ ] **Step 1: Present the report to Juliana**

Show `tools/folder_dedup_report.md`: staged count, by-year, by-domain, and the near-duplicate list. Ask her to confirm the near-dups are genuinely new (or tell me which to drop).

- [ ] **Step 2: Apply her decisions**

For any titles she flags as dups, remove them from `tools/folder_new_articles.json` (by exact title match) and note the removals. Re-run Step 3 integrity check from Task 2.

- [ ] **Step 3: Gate**

Do **not** proceed to Task 5 (catalog merge) until Juliana says the worklist is clean. (MCQ generation in Task 4 may run in parallel with this review since it doesn't touch the catalog.)

---

## Task 4: MCQ + domain workflow for folder articles

**Files:**
- Create: `tools/workflows/folder_mcqs.workflow.js`
- Produces: `tools/qa_fixes/folder_batch_<N>.json` — each a list of full catalog records (with `mcqs` filled, `suggested_*` resolved to `domain`/`subdomain_page`, `id` slug, `citation`).

**Interfaces (record the agent must emit per article):** `{id, title, authors, journal, year, citation, doi, source:"folder", abstract, abstract_origin:"spreadsheet", domain, subdomain_page, mcqs:[{q,o[4],a,e}, ...]}`.

- [ ] **Step 1: Write the Workflow script**

```javascript
export const meta = {
  name: 'folder-mcqs',
  description: 'Domain-assign + write & verify 2-3 MCQs for each new folder article',
  phases: [{ title: 'Write' }, { title: 'Verify' }],
}
// args = { total: <int>, batchSize: <int> }  (the worklist is read from disk by agents)
const total = args.total, B = args.batchSize || 20
const RECORD_SCHEMA = {
  type: 'object',
  properties: {
    records: { type: 'array', items: { type: 'object',
      required: ['id','title','authors','journal','year','citation','doi','source','abstract','abstract_origin','domain','subdomain_page','mcqs'],
      properties: {
        id:{type:'string'}, title:{type:'string'}, authors:{type:'string'}, journal:{type:'string'},
        year:{type:'integer'}, citation:{type:'string'}, doi:{type:'string'}, source:{type:'string'},
        abstract:{type:'string'}, abstract_origin:{type:'string'}, domain:{type:'string'}, subdomain_page:{type:'string'},
        mcqs:{type:'array', items:{type:'object', required:['q','o','a','e'],
          properties:{q:{type:'string'}, o:{type:'array', items:{type:'string'}}, a:{type:'integer'}, e:{type:'string'}}}}
      } } }
  }, required: ['records']
}
const batches = []
for (let s = 0; s < total; s += B) batches.push([s, Math.min(s + B, total)])
const results = await pipeline(
  batches,
  ([s, e], _orig, i) => agent(
    `Read \`tools/folder_new_articles.json\` and process records at indices ${s}..${e-1} (inclusive start, exclusive end).
For EACH article emit one catalog record:
- Copy title/authors/journal/year/abstract verbatim. If 'journal' is empty but the authors field looks like "Lastname, Journalname", split it sensibly.
- doi: "" (unknown). citation: "<authors>. <title>. <journal>. <year>." abstract_origin: "spreadsheet". source: "folder".
- domain/subdomain_page: START from suggested_domain/suggested_page, but CORRECT it from the abstract if clearly mis-routed. subdomain_page MUST be one of the existing files under the repo (verify with: ls of the folder).
- id: slug "<firstauthorlastname>-<year>-<3-4 title words>", lowercase-hyphen, unique within your batch.
- mcqs: write 2-3 CLOSED-BOOK, conclusion-focused MCQs answerable from the ABSTRACT ALONE. Each: a stem, exactly 4 options, integer answer index 0-3, and a one-sentence rationale 'e'. Match the terse house style of existing hub MCQs.
Return {records:[...]}.`,
    { label: `write:${s}-${e}`, phase: 'Write', schema: RECORD_SCHEMA }
  ),
  (written, [s, e], i) => agent(
    `Adversarially verify these ${written?.records?.length||0} catalog records (JSON below). For EACH MCQ confirm: (1) the answer index 'a' is correct, (2) it is answerable from that article's abstract alone, (3) exactly 4 options, no ambiguous/duplicate options, (4) rationale matches the keyed answer. FIX any problem in place (rewrite stem/options/answer/rationale). Also confirm subdomain_page is an existing repo file. Then WRITE the corrected array to \`tools/qa_fixes/folder_batch_${i}.json\` using your Write tool, and return {written: <count>, file: "tools/qa_fixes/folder_batch_${i}.json"}.\n\nRECORDS:\n${JSON.stringify(written?.records||[])}`,
    { label: `verify:${s}-${e}`, phase: 'Verify',
      schema: { type:'object', required:['written','file'], properties:{ written:{type:'integer'}, file:{type:'string'} } } }
  )
)
const ok = results.filter(Boolean)
log(`folder MCQ workflow: ${ok.length}/${batches.length} batches wrote partials`)
return { batches: batches.length, partials: ok }
```

- [ ] **Step 2: Determine `total` and run the workflow**

Get the count: `python3 -c "import json;print(len(json.load(open('tools/folder_new_articles.json'))))"`.
Invoke the Workflow tool with `scriptPath: "tools/workflows/folder_mcqs.workflow.js"` and `args: {total: <count>, batchSize: 20}`.
Expected: a `<task-notification>` on completion; `tools/qa_fixes/folder_batch_*.json` files created (~30–33 of them).

- [ ] **Step 3: Verify partials parse and carry MCQs**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
python3 -c "
import json,glob
recs=[r for f in glob.glob('tools/qa_fixes/folder_batch_*.json') for r in json.load(open(f))]
print('records',len(recs))
print('all 2-3 mcqs', all(2<=len(r['mcqs'])<=3 for r in recs))
print('opts==4', all(len(m['o'])==4 for r in recs for m in r['mcqs']))
print('ans range', all(0<=m['a']<4 for r in recs for m in r['mcqs']))
"
```
Expected: `records` ≈ worklist count, all three checks `True`.

- [ ] **Step 4: Commit the workflow script + partials**

```bash
cd ~/abvp-study && git add tools/workflows/folder_mcqs.workflow.js tools/qa_fixes/folder_batch_*.json && git commit -m "feat(journal): generate + verify MCQs for folder articles via workflow"
```

---

## Task 5: Merge partials → catalog, validate, build, per-domain deploy

**Files:**
- Create: `tools/merge_partials.py`
- Modify: `tools/journal-catalog.json`

**Interfaces:**
- Consumes: `tools/qa_fixes/folder_batch_*.json`, `lib_catalog.validate_record`/`load_catalog`/`save_catalog`.

- [ ] **Step 1: Write `tools/merge_partials.py`**

```python
#!/usr/bin/env python3
"""Merge workflow partials into journal-catalog.json after full validation."""
import json, glob, sys, re
from pathlib import Path
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from lib_catalog import load_catalog, save_catalog, validate_record

def main(pattern):
    cat = load_catalog(str(TOOLS/"journal-catalog.json"))
    have_titles = {re.sub(r"[^a-z0-9]","",r["title"].lower()) for r in cat}
    have_ids = {r["id"] for r in cat}
    new = [r for f in sorted(glob.glob(str(TOOLS/pattern))) for r in json.load(open(f))]
    added, problems = [], []
    for r in new:
        n = re.sub(r"[^a-z0-9]","",r["title"].lower())
        if n in have_titles: continue           # last-line dedup safety
        base = r["id"]; k = 1
        while r["id"] in have_ids: r["id"] = f"{base}-{k}"; k += 1
        errs = validate_record(r)
        if errs: problems.append((r.get("title","?"), errs)); continue
        have_titles.add(n); have_ids.add(r["id"]); added.append(r)
    if problems:
        for t,e in problems[:20]: print("INVALID:", t, e)
        print(f"\n{len(problems)} invalid records — fix partials and re-run. Nothing written."); sys.exit(1)
    save_catalog(str(TOOLS/"journal-catalog.json"), cat + added)
    print(f"appended {len(added)} records; catalog now {len(cat)+len(added)}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "qa_fixes/folder_batch_*.json")
```

- [ ] **Step 2: Dry-validate before writing**

Run: `export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && python3 tools/merge_partials.py "qa_fixes/folder_batch_*.json"`
Expected: either `appended N records...` OR an `INVALID:` list. If invalid, fix the offending `folder_batch_*.json` (or re-run the Verify agent on that batch) and repeat until it appends.

- [ ] **Step 3: Full-catalog validation**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
python3 -c "
import sys;sys.path.insert(0,'tools')
from lib_catalog import load_catalog, validate_record
c=load_catalog('tools/journal-catalog.json');bad=0
for r in c:
    e=validate_record(r)
    if e: bad+=1;print(r.get('id'),e)
print('total',len(c),'invalid',bad)
"
```
Expected: `invalid 0`, total ≈ 174 + folder count.

- [ ] **Step 4: Rebuild pages + mock exam**

Run: `export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && python3 tools/build_journal_sections.py && python3 tools/build_mock_journal.py`
Expected: per-page `[OK]` lines; no `[SKIP]` for pages that now have records.

- [ ] **Step 5: Sanity-check rendered pages**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
git diff --stat | tail -20
grep -l "JOURNAL-ARTICLES:START" physical-health/infectious_disease_hub.html
python3 -c "import glob; [print('unclosed?',f) for f in glob.glob('physical-health/*.html') if open(f).read().count('JOURNAL-ARTICLES:START')!=open(f).read().count('JOURNAL-ARTICLES:END')]"
```
Expected: changed HTML files listed; marker present; no `unclosed?` output.

- [ ] **Step 6: Commit per domain & push**

Commit changed pages grouped by domain folder, then push:
```bash
cd ~/abvp-study
git add tools/merge_partials.py tools/journal-catalog.json
git add physical-health/ && git commit -m "feat(journal): add folder articles — Physical Health (abstracts + MCQs)"
git add companion-animal-homelessness/ && git commit -m "feat(journal): add folder articles — Companion Animal Homelessness"
git add behavioral-health/ && git commit -m "feat(journal): add folder articles — Behavioral Health"
git add shelter-management/ && git commit -m "feat(journal): add folder articles — Shelter Management"
git add community-public-health/ research-biostats/ animals-public-policy/ && git commit -m "feat(journal): add folder articles — remaining domains + mock exam"
git push
```
Expected: pushes succeed; GitHub Pages live within ~1 min.

---

## Task 6: Diplomate roster + 2025–2026 discovery workflow

**Files:**
- Create: `tools/workflows/discovery_2025_2026.workflow.js`
- Produces: `tools/discovery_2025_2026/diplomate_roster.json`, `tools/discovery_2025_2026/cand_<N>.json` partials.

**Interfaces:**
- Candidate record: `{diplomate, journal, year(2025|2026), authors, title, abstract, takeaways, topic_tab}` where `topic_tab` ∈ {`Diplomate Publications`,`Misc`,`Behaviour`,`Infectious Disease`}.

- [ ] **Step 1: Seed the roster file from the existing spreadsheet**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && mkdir -p tools/discovery_2025_2026
python3 -c "
import openpyxl,json
p='/Users/jxue/Library/CloudStorage/Dropbox/work docs/protocols in interactive dashboards/ABVP exam hub/2026 ABVP shelter medicine study/JOURNAL REVIEW/SPREADSHEETS/2025 Diplomate publications spreadsheet.xlsx'
ws=openpyxl.load_workbook(p,read_only=True,data_only=True)['Diplomate Publications']
names=sorted({str(r[0]).strip() for r in ws.iter_rows(min_row=2,values_only=True) if r and r[0] and str(r[0]).strip()})
json.dump({'seed':names,'added':[]},open('tools/discovery_2025_2026/diplomate_roster.json','w'),indent=2)
print(len(names),'seed diplomates')
"
```
Expected: `49 seed diplomates`.

- [ ] **Step 2: Cross-check the official ABVP Shelter Medicine diplomate directory**

Use WebSearch/WebFetch for the current ABVP Shelter Medicine Practice diplomate directory. Add any names not in `seed` to the `added` list in `diplomate_roster.json`. (If the directory is inaccessible, log that the roster is seed-only and proceed.)

- [ ] **Step 3: Write the discovery Workflow script**

```javascript
export const meta = {
  name: 'discovery-2025-2026',
  description: 'Find 2025-2026 shelter-med articles: per-diplomate + topic sweep',
  phases: [{ title: 'Diplomates' }, { title: 'Topics' }],
}
// args = { roster: [<names>], topics: ["Misc","Behaviour","Infectious Disease"] }
const CAND_SCHEMA = { type:'object', required:['candidates'], properties:{ candidates:{ type:'array', items:{
  type:'object', required:['diplomate','journal','year','authors','title','abstract','takeaways','topic_tab'],
  properties:{ diplomate:{type:'string'}, journal:{type:'string'}, year:{type:'integer'},
    authors:{type:'string'}, title:{type:'string'}, abstract:{type:'string'}, takeaways:{type:'string'}, topic_tab:{type:'string'} } } } } }
const roster = args.roster, topics = args.topics
phase('Diplomates')
const dip = await parallel(roster.map((name, i) => () => agent(
  `Search PubMed and Google Scholar for journal articles published in 2025 or 2026 by "${name}", a Diplomate of ABVP (Shelter Medicine Practice). For each genuine 2025-2026 article return: diplomate="${name}", journal, year, authors (full list), title, abstract (fetch the real abstract; if truly unavailable, a 2-sentence summary and note "[summary]"), takeaways (1-2 exam-relevant points), topic_tab="Diplomate Publications". Only 2025-2026. Return {candidates:[...]} (empty if none).`,
  { label: `dip:${name}`, phase: 'Diplomates', schema: CAND_SCHEMA })))
phase('Topics')
const top = await parallel(topics.map((t, i) => () => agent(
  `Search for shelter/community animal-health journal articles published in 2025 or 2026 on the theme "${t}". Cover JSMCAH, JFMS, JAVMA, JSAP, Animals (MDPI), Frontiers in Vet Science, Vet Record. For each: diplomate="" (unless an author is an ABVP shelter-med diplomate, then their name), journal, year, authors, title, real abstract, takeaways, topic_tab="${t}". Only 2025-2026. Aim for breadth. Return {candidates:[...]}.`,
  { label: `topic:${t}`, phase: 'Topics', schema: CAND_SCHEMA })))
const all = [...dip, ...top].filter(Boolean).flatMap(r => r.candidates)
return { candidates: all }
```

- [ ] **Step 4: Run the workflow and persist candidates**

Read the roster, then invoke Workflow with `scriptPath: "tools/workflows/discovery_2025_2026.workflow.js"` and `args: {roster: [...all roster names...], topics: ["Misc","Behaviour","Infectious Disease"]}`. The workflow returns `{candidates:[...]}` in the task result; write that array to `tools/discovery_2025_2026/cand_all.json`.
Expected: a non-trivial candidate list spanning the 4 tabs.

- [ ] **Step 5: Dedup candidates against the live hub**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
python3 -c "
import json,re,sys;sys.path.insert(0,'tools')
from lib_catalog import load_catalog
norm=lambda s:re.sub(r'[^a-z0-9]','',str(s).lower())
have={norm(r['title']) for r in load_catalog('tools/journal-catalog.json')}
c=json.load(open('tools/discovery_2025_2026/cand_all.json'))
seen=set();out=[]
for r in c:
    n=norm(r['title'])
    if n in have or n in seen: continue
    seen.add(n);out.append(r)
json.dump(out,open('tools/discovery_2025_2026/cand_deduped.json','w'),ensure_ascii=False,indent=2)
print('candidates',len(c),'-> after dedup',len(out))
"
```
Expected: prints counts; `cand_deduped.json` written.

- [ ] **Step 6: Commit**

```bash
cd ~/abvp-study && git add tools/workflows/discovery_2025_2026.workflow.js tools/discovery_2025_2026/ && git commit -m "feat(journal): 2025-2026 diplomate + topic discovery candidates"
```

---

## Task 7: Build the 4-tab 2025–2026 review spreadsheet

**Files:**
- Create: `tools/build_review_spreadsheet.py`
- Produces: `2025-2026-shelter-med-articles.xlsx` (repo root).

- [ ] **Step 1: Write `tools/build_review_spreadsheet.py`**

```python
#!/usr/bin/env python3
"""Build the 4-tab 2025-2026 review spreadsheet (format follows 2025 Diplomate sheet)."""
import json, sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font
TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
TABS = ["Diplomate Publications", "Misc", "Behaviour", "Infectious Disease"]
HEADERS = ["Diplomate", "Journal", "Year", "Author", "Title", "Abstract", "Takeaways"]

def main():
    cands = json.load(open(TOOLS/"discovery_2025_2026/cand_deduped.json"))
    wb = openpyxl.Workbook(); wb.remove(wb.active)
    for tab in TABS:
        ws = wb.create_sheet(tab[:31])
        ws.append(HEADERS)
        for c in ws[1]: c.font = Font(bold=True)
        rows = [r for r in cands if r.get("topic_tab") == tab]
        rows.sort(key=lambda r: (-int(r.get("year",0)), str(r.get("title",""))))
        for r in rows:
            ws.append([r.get("diplomate",""), r.get("journal",""), r.get("year",""),
                       r.get("authors",""), r.get("title",""), r.get("abstract",""), r.get("takeaways","")])
        widths = [22, 18, 6, 28, 50, 80, 50]
        for i, w in enumerate(widths, 1): ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    wb.save(ROOT/"2025-2026-shelter-med-articles.xlsx")
    print("wrote 2025-2026-shelter-med-articles.xlsx with tabs:", TABS)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run + verify tab counts**

Run:
```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study && python3 tools/build_review_spreadsheet.py
python3 -c "
import openpyxl;wb=openpyxl.load_workbook('2025-2026-shelter-med-articles.xlsx',read_only=True)
for s in wb.sheetnames:print(s, wb[s].max_row-1,'rows', [c.value for c in next(wb[s].iter_rows(max_row=1))])
"
```
Expected: 4 tabs listed with the 7 `HEADERS` and per-tab row counts; all years 2025/2026.

- [ ] **Step 3: Commit**

```bash
cd ~/abvp-study && git add tools/build_review_spreadsheet.py "2025-2026-shelter-med-articles.xlsx" && git commit -m "feat(journal): build 2025-2026 review spreadsheet (4 tabs)"
```

---

## Task 8: REVIEW GATE — 2025–2026 spreadsheet (human checkpoint)

**Files:** `2025-2026-shelter-med-articles.xlsx`.

- [ ] **Step 1: Deliver the spreadsheet to Juliana**

Tell her the path, the per-tab counts, and how many diplomates were covered (seed 49 + any added). Ask her to review and mark which articles to include on the hub (e.g., delete rows she doesn't want, or tell me which tabs/rows to take).

- [ ] **Step 2: Gate**

Do **not** add any 2025–2026 article to the hub until she approves the subset.

---

## Task 9: Fold approved 2025–2026 articles into the hub

**Files:**
- Modify: `tools/journal-catalog.json`
- Reuse: `tools/workflows/folder_mcqs.workflow.js` (same MCQ pipeline), `tools/merge_partials.py`.

- [ ] **Step 1: Stage the approved rows**

From Juliana's reviewed spreadsheet, build `tools/discovery_2025_2026/approved.json` — a worklist in the SAME shape as `folder_new_articles.json` but `source:"discovered"`, `abstract_origin:"pubmed"` (or `"web"`), with `suggested_domain`/`suggested_page` set from each row's `topic_tab` + abstract.

```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
# Read the reviewed xlsx, keep rows still present, write approved.json with source="discovered".
# (Script mirrors extract_folder_articles staging fields; topic_tab -> suggested_domain/page.)
```

- [ ] **Step 2: Run the MCQ workflow on the approved set**

Point the agents at `tools/discovery_2025_2026/approved.json` (copy it to where the workflow expects, or pass its path in the prompt) and run `folder_mcqs.workflow.js` with `args:{total:<approved count>, batchSize:15}`, writing `tools/qa_fixes/disc_batch_*.json`. Ensure each emitted record has `source:"discovered"`.

- [ ] **Step 3: Merge, validate, build, deploy**

```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
python3 tools/merge_partials.py "qa_fixes/disc_batch_*.json"
python3 -c "import sys;sys.path.insert(0,'tools');from lib_catalog import load_catalog,validate_record;c=load_catalog('tools/journal-catalog.json');print('invalid',sum(1 for r in c if validate_record(r)))"
python3 tools/build_journal_sections.py && python3 tools/build_mock_journal.py
git add tools/journal-catalog.json tools/qa_fixes/disc_batch_*.json physical-health/ companion-animal-homelessness/ behavioral-health/ shelter-management/ community-public-health/ research-biostats/ animals-public-policy/
git commit -m "feat(journal): add approved 2025-2026 discovered articles (abstracts + MCQs)"
git push
```
Expected: `invalid 0`; push succeeds.

---

## Task 10: Update memory + final verification

**Files:**
- Modify: `~/.claude/projects/-Users-jxue/memory/project_journal_abstracts_hub.md`, `MEMORY.md`.

- [ ] **Step 1: Verify live counts**

```bash
export PATH="/opt/homebrew/bin:$PATH"; cd ~/abvp-study
python3 -c "import json;from collections import Counter;d=json.load(open('tools/journal-catalog.json'));print('total',len(d));print('by year',dict(sorted(Counter(r['year'] for r in d).items())));print('by source',dict(Counter(r['source'] for r in d)))"
```
Expected: total ≈ 174 + folder + approved; 2025/2026 counts increased.

- [ ] **Step 2: Update the project memory file**

Update `project_journal_abstracts_hub.md` with the new total article count, the folder-integration date (2026-06-27), the new tooling (`extract_folder_articles.py`, `lib_extract.py`, `build_review_spreadsheet.py`, `merge_partials.py`, the two workflow scripts), and the location of `2025-2026-shelter-med-articles.xlsx`. Refresh the `MEMORY.md` one-line pointer.

- [ ] **Step 3: Commit**

```bash
cd ~/abvp-study && git add -A && git commit -m "docs(journal): folder integration + 2025-2026 discovery complete" && git push
```

---

## Self-Review notes (coverage map)

- Spec §4 extraction/dedup → Tasks 1–2. §6 review gate → Task 3. §5 MCQ workflow → Task 4. §6 merge/build/deploy → Task 5. §8.1 roster → Task 6 Steps 1–2. §8.2 topic discovery → Task 6 Step 3. §8.3 4-tab spreadsheet (format = `Diplomate|Journal|Year|Author|Title|Abstract|Takeaways`) → Task 7. §8.4 review gate + hub fold → Tasks 8–9. §9 deliverables + memory → Task 10.
- Year guards: Task 2 enforces 2021–2024; Task 6 prompts enforce 2025–2026; `validate_record` enforces 2021–2026 globally.
- Dedup appears three times (Task 2 vs catalog, Task 5 last-line safety, Task 6 Step 5 for discovery) — intentional defense in depth.
