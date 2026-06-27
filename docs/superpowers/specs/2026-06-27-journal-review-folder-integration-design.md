# Journal Review Folder → ABVP Hub Integration + 2025–2026 Discovery

**Date:** 2026-06-27
**Repo:** `~/abvp-study` (canonical/live; Dropbox HTML copies are stale)
**Status:** Design — awaiting sign-off

---

## 1. Overview & Goals

Two related deliverables:

1. **Fold the JOURNAL REVIEW folder into the hub.** Extract every new 2021–2024
   journal article from Juliana's 5 board-review spreadsheets, de-duplicate against
   the 174 articles already on the hub, and add the survivors (~645) each with an
   abstract **and 2–3 MCQs**, using the existing catalog-driven build pipeline.
   Folder additions pass through a **duplicate-review gate** before going live.

2. **Build a current 2025–2026 article list.** The folder contains essentially no
   new 2025–2026 articles, so run a fresh web-discovery pass — with **comprehensive
   coverage of every ABVP Shelter Medicine specialist's** 2025–26 publications
   (those are the examinable ones) — and compile a single multi-tab `.xlsx` review
   spreadsheet for Juliana's sign-off. Approved entries are then folded into the hub
   via the same pipeline.

### Source of the requirement

- Folder: `…/ABVP exam hub/2026 ABVP shelter medicine study/JOURNAL REVIEW/`
  - `SPREADSHEETS/` — 5 active board-review workbooks (~1,230 rows, abstracts written)
  - `ARTICLES/` — 68 PDFs (2016–2023 review chapters/forensics; no recent content)
  - `Journal of Shelter Medicine and Community Animal Health - ABVP exam.docx` — curated list (mostly 2022–2024)
- Hub catalog: `~/abvp-study/tools/journal-catalog.json` — 174 records, years 2021–2026.

### Reconnaissance findings (already verified)

- Spreadsheet rows total **1,230**; **784** are 2021–2026; after dedup against the
  174 hub records, **645 are new** — distributed **2021:126, 2022:227, 2023:147,
  2024:145, and ZERO new 2025–2026**. 644/645 already carry an abstract.
- ARTICLES PDFs are 2016–2023 review chapters — out of scope (not recent journal research).
- The master docx's handful of 2025–26 items are already on the hub.
- The Diplomate spreadsheet already names **49 ABVP shelter-med diplomates** (seed roster).

---

## 2. Scope

### In scope
- All **645 new 2021–2024** articles from the 5 active spreadsheets → hub (abstract + 2–3 MCQs).
- Duplicate-review report for the 645 (review gate before push).
- Web discovery of new **2025–2026** articles, emphasis on ABVP diplomate publications.
- One multi-tab `.xlsx` review spreadsheet (2025–2026 only).
- Approved 2025–2026 articles → hub via the same pipeline (after sign-off).

### Out of scope
- ARTICLES/ PDF review chapters (2016–2023) and forensics PDFs.
- Pre-2021 spreadsheet rows.
- Any hand-editing of subdomain HTML (pipeline regenerates it).
- Re-writing/relocating existing 174 records.

---

## 3. Architecture — reuse the existing catalog-driven pipeline

`tools/journal-catalog.json` is the single source of truth. Adding an article =
appending a valid record, then running the build scripts. **No HTML is hand-edited.**

```
spreadsheets ──Stage0(py)──► folder_new_articles.json  ──Stage1(workflow)──► validated records
                                   │                                              │
                              dedup report  ◄── REVIEW GATE (Juliana)             ▼
                                                                       append → journal-catalog.json
                                                                                  │
                                                            build_journal_sections.py  (panels + MCQ banks)
                                                            build_mock_journal.py       (mock exam)
                                                                                  │
                                                                       git commit/push per domain → live
```

Record schema (enforced by `lib_catalog.validate_record`): `id, title, authors,
journal, year(2021–2026), citation, doi(""ok), source("folder"|"discovered"),
abstract(non-empty), abstract_origin, domain, subdomain_page(must resolve to a real
file), mcqs[]`. Each MCQ = `{q, o[4], a(0–3), e}`.

---

## 4. Stage 0 — Deterministic extraction & dedup (plain Python, no agents)

Script `tools/extract_folder_articles.py`:

1. Read the 5 active workbooks; per sheet normalize to `{year, authors, journal,
   title, abstract, key_points, source_sheet}`.
2. Filter to year 2021–2026.
3. **Dedup** against `journal-catalog.json` and within the folder:
   - Primary key: normalized title (lowercased, alphanumerics only).
   - Secondary: first-author + year.
   - Fuzzy near-duplicates (similarity 0.80–0.99) are **not auto-dropped** — they go
     to a side-list for Juliana's eye.
4. Assign a **suggested** `domain` + `subdomain_page` from the sheet→page map (§7).
5. Emit:
   - `tools/folder_new_articles.json` — staged records (abstracts populated, `source:"folder"`, `mcqs:[]`).
   - `tools/folder_dedup_report.md` + `.xlsx` — exact dups dropped, near-dup side-list, and the clean worklist count by year/domain.

---

## 5. Stage 1 — Domain assignment + MCQ writing (multi-agent workflow)

Batch `folder_new_articles.json` by `source_sheet`/topic (~15–40 articles each).
Per batch, a 2-stage pipeline:

- **Write agent:** for each article, confirm `domain`/`subdomain_page` (sheet hint +
  abstract), and write **2–3 closed-book, conclusion-focused MCQs from the abstract
  only**, matching house style (`q`, 4 options, answer index `a`, rationale `e`).
- **Verify agent (adversarial):** checks each MCQ — answer is correct, answerable
  from the abstract alone, options unambiguous, exactly 4 — and fixes or flags.

Returns validated records (schema-conformant). Batches run in topic waves.

---

## 6. Stage 2 — Merge, build, **duplicate-review gate**, deploy

1. Append validated records (unique `id` slugs) to `journal-catalog.json`.
2. Run `validate_record` across the whole catalog — must be 0 problems.
3. **REVIEW GATE:** present `folder_dedup_report` + the per-domain new-article counts
   to Juliana to confirm there are no duplicates **before** pushing live.
4. On confirmation: run `build_journal_sections.py` + `build_mock_journal.py`,
   sanity-check (markers present, pages parse), then `git commit`/`push`
   **per domain** so progress is incremental and reviewable.

---

## 7. Sheet → domain/page mapping (Stage 0 seed; agent refines per-article)

| Source sheet(s) | domain → subdomain_page |
|---|---|
| CIRDC, CPV, FPV, FIV.FeLV, Feline URI, SARS-CoV-2, FIP.FeCoV, Dermatophytosis, Other (ID) | Physical Health → `physical-health/infectious_disease_hub.html` |
| Heartworm, Parasitology | Physical Health → `physical-health/parasites_hub.html` |
| AnesthesiaAnalgesia | Physical Health → `physical-health/surgery_anesthesia_hub.html` |
| SpayNeuter Surgery, Agebenefits of SpayNeuter | Companion Animal Homelessness → `companion-animal-homelessness/spay_neuter_hub_2.html` |
| SNRTNR | Companion Animal Homelessness → `companion-animal-homelessness/nonsurgical_sterilization_hub.html` |
| Outreach for Owned Animals | Companion Animal Homelessness → `companion-animal-homelessness/access_vet_care_hub.html` |
| Transport | Companion Animal Homelessness → `companion-animal-homelessness/animal_transport_relocation_hub.html` |
| Disaster | Companion Animal Homelessness → `companion-animal-homelessness/disaster_emergency_hub.html` |
| Mgmt stats design sanitation | Shelter Management → `shelter-management/05_data_analysis.html` (sanitation→`physical-health/sanitation_biosecurity_hub.html`) |
| Mental health | Shelter Management → `shelter-management/06_mental_health.html` |
| Forensicscrueltyhoarding | Community & Public Health → `community-public-health/01_animal_cruelty.html` / `01e_hoarding.html` |
| Public Health / One Health / Zoonoses | Community & Public Health → `community-public-health/02_zoonotic_disease.html` / `04_rabies.html` |
| K9/Fel Behaviour & Training, assessments, Psychopharm & pheromones | Behavioral Health → `behavioral-health/*` (training/bmod, assessment, meds) |
| WelfareHousingC4C, IntakeOutcomeLOS | Shelter Mgmt / Behavioral Health (QOL, housing, LOS) |
| Pediatrics, Small mammal/exotic/farm, General Medicine | Physical Health → `medical_health_hub.html` / `nutrition_husbandry_hub.html` / `other-animals_hub.html` |
| Diplomate Publications, ABVP Journal Club, Misc | route per-article by abstract topic |

The agent makes the final per-article call; the table just seeds Stage 0.

---

## 8. Stage 3 — 2025–2026 discovery → multi-tab review spreadsheet (review-gated)

### 8.1 Diplomate roster (comprehensive)
- Seed from the **49 names** in the existing Diplomate spreadsheet.
- Cross-check against the **official ABVP Shelter Medicine Practice diplomate
  directory** (web) to add anyone missing/newly boarded.
- For each diplomate, search PubMed + Scholar for **2025–2026** publications.

### 8.2 Topic discovery
Beyond diplomates, sweep 2025–2026 shelter/community-animal-health literature
across JSMCAH, JFMS, JAVMA, JSAP, Animals, Frontiers Vet Sci, etc., deduped against
the hub. Fetch each abstract.

### 8.3 Deliverable — one `.xlsx`, four tabs
`2025-2026-shelter-med-articles.xlsx` with tabs (split as requested):
**Diplomate Publications · Misc · Behaviour · Infectious Disease**.

Each tab follows the **2025 Diplomate publications spreadsheet** format:

| Diplomate | Journal | Year | Author | Title | Abstract | Takeaways |
|---|---|---|---|---|---|---|

(`Diplomate` = the ABVP shelter-med diplomate author where applicable, else blank;
`Takeaways` = short exam-relevant key points. Column set mirrors the source; final
columns confirmable on spec review.)

### 8.4 Review gate → hub
Juliana reviews the spreadsheet and marks which articles to include. Approved
articles run through Stage 1–2 (`source:"discovered"`) and go live on the hub.

---

## 9. Deliverables checklist
- [ ] `tools/extract_folder_articles.py` + `tools/folder_new_articles.json`
- [ ] `tools/folder_dedup_report.md` / `.xlsx` (duplicate-review gate)
- [ ] ~645 new `source:"folder"` records → live hub (panels, MCQ banks, mock exam)
- [ ] `2025-2026-shelter-med-articles.xlsx` (4 tabs; diplomate-comprehensive)
- [ ] Approved 2025–26 `source:"discovered"` records → live hub (after sign-off)
- [ ] Memory/project files updated (`project_journal_abstracts_hub.md`)

---

## 10. Risks & mitigations
- **Dedup false-negatives** (same article, different title) → fuzzy side-list + the
  explicit duplicate-review gate before push.
- **MCQ correctness** → adversarial verify stage; answerable-from-abstract rule.
- **Domain mis-routing** → sheet-seeded mapping + per-article agent confirmation.
- **Scale (645)** → topic waves, per-domain commits, incremental review.
- **Missing diplomates** → official-directory cross-check, not just the 49 seed names.
- **Token cost of the workflow** → Juliana has explicitly opted into multi-agent orchestration.

---

## 11. Out of scope / future
- ARTICLES/ PDF review chapters as catalog entries.
- Pre-2021 spreadsheet rows.
- Synthesized cross-study MCQs for the new articles (existing `synthesized_mcqs.json` untouched).
