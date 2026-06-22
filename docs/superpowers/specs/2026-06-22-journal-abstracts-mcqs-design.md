# Journal Abstracts + MCQs → ABVP Study Hub — Design Spec

**Date:** 2026-06-22
**Author:** Juliana (with Claude)
**Status:** Draft for review

## Goal

Surface the journal-article content that the 2026 SMP RVS exam can draw from, directly inside the ABVP study hub. The exam rules (per *SMP RVS Exam Study Guide 2026*, Journals section) are:

1. Items come from journals on the RVS Reading List (23 journals; core journal = *Journal of Shelter Medicine and Community Animal Health*, JSMCAH).
2. The question is drawn from **the abstract only**.
3. The abstract must be **freely available**.
4. **5-year lookback.** Study guide says 2021–2025; per Juliana's instruction we also include **2026**.

For each in-scope article, add to the hub: full citation + the real abstract + 2–3 single-best-answer MCQs (answer + rationale).

## Scope

### In scope
- All ~85 PDFs in `Dropbox/.../ABVP specialist pathway/reading list/journal article/`.
- Gap-discovery of articles not in that folder:
  - **JSMCAH (core journal):** complete enumeration of 2021–2026 issues; every shelter-relevant article with a free abstract.
  - **Other 22 journals:** best-effort *targeted* search for shelter-medicine-relevant articles 2021–2026 with free abstracts.
- Mapping each article to the best-fit subdomain page across all 7 hub domains.
- 2–3 MCQs per article, derived strictly from the abstract.

### Out of scope
- Exhaustive enumeration of the 22 general journals (infeasible — they are large and mostly non-shelter). Coverage there is best-effort and will be logged, not guaranteed complete.
- Full-text content beyond the abstract (exam tests abstract only; exception in study guide is Vet Clinics of North America, not on the journal list here).
- Articles for which no genuine free abstract can be obtained — excluded, never fabricated.

## Core principles

- **No fabrication.** Abstracts are extracted from the folder PDFs or fetched verbatim/faithfully from a free source (PubMed, journal site, DOI). If no free abstract is obtainable, the article is dropped and logged.
- **Abstract-only MCQs.** Every MCQ must be answerable from the abstract text alone — mirroring how the exam writes items. No facts pulled from full text or outside knowledge.
- **Single source of truth.** A `journal-catalog.json` holds every article's metadata, abstract, subdomain mapping, and MCQs. The hub pages are *generated* from it, so format changes = regenerate, not hand-edit.

## Architecture

### Data model — `tools/journal-catalog.json`
Array of article records:
```
{
  "id": "slug-unique",
  "title": "...",
  "authors": "...",
  "journal": "JSMCAH",
  "year": 2024,
  "citation": "Authors. Title. Journal. Year;vol(iss):pp.",
  "doi": "10.xxxx/...",            // if known
  "source": "folder" | "discovered",
  "abstract": "verbatim/faithful abstract text",
  "abstract_origin": "pdf:<filename>" | "url:<source>",
  "domain": "physical-health",
  "subdomain_page": "physical-health/surgery_anesthesia_hub.html",
  "mcqs": [
    {"q":"stem","o":["a","b","c","d"],"a":2,"e":"rationale (abstract-grounded)"}
  ]
}
```

### Pipeline phases
1. **Extract** — read each folder PDF, pull citation + abstract, assign domain/subdomain → catalog (`source:"folder"`).
2. **Discover** — JSMCAH 2021–2026 full diff vs. folder; targeted searches across other 22 journals; fetch real abstracts → catalog (`source:"discovered"`). Log anything skipped (no free abstract).
3. **MCQs** — generate 2–3 abstract-grounded MCQs per article into the catalog.
4. **Inject** — generator script (`tools/build_journal_sections.py`) reads catalog, renders a styled **"Additional Resources → Journal Articles"** block per page, appends to the matching subdomain HTML. Block is idempotent (delimited markers so re-runs replace, not duplicate).
5. **Ship** — commit + push (Pages auto-deploys).

### Page rendering (per subdomain page)
- A new section, appended near the end of the page content, headed **Additional Resources** → subsection **Journal Articles (2021–2026)**.
- Each article = a card matching the page's existing CSS (`.card`/`.box` style):
  - Citation (bold title, authors, journal·year).
  - Abstract text.
  - 2–3 MCQs, each with options and a **Show answer** toggle revealing correct option + rationale.
- Self-contained vanilla JS toggle (no dependency on the page's existing quiz `Q` array — that quiz is left untouched).
- Delimited by `<!-- JOURNAL-ARTICLES:START --> ... <!-- JOURNAL-ARTICLES:END -->` for idempotent regeneration.

## Validation / rollout

- **Pilot:** `physical-health/surgery_anesthesia_hub.html` built first (folder has many surgery/anesthesia abstracts). Juliana reviews rendered format + sample MCQs.
- On approval, roll out catalog-driven generation to all subdomain pages.
- Discovery (Phase 2) for the 22 general journals runs as a best-effort pass; a coverage log records what was searched and what was skipped so gaps are visible.

## Domain → page mapping (reference)

| Domain | Folder |
|---|---|
| Physical Health | `physical-health/` (infectious_disease, sanitation_biosecurity, surgery_anesthesia, vaccination, facility_shelter_design, euthanasia, medical_health, nutrition_husbandry, parasites) |
| Shelter Management | `shelter-management/` (population, animal_id_tracking, mgmt_leadership, record_keeping, data_analysis, regulatory, mental_health, resource_allocation, liability) |
| Behavioral Health | `behavioral-health/` |
| Companion Animal Homelessness | `companion-animal-homelessness/` |
| Community & Public Health | `community-public-health/` |
| Animals & Public Policy | `animals-public-policy/` |
| Research & Biostats | `research-biostats/` |

## Risks / open items
- Discovery breadth for 22 journals is inherently incomplete — set expectation, log coverage.
- Abstract fetching depends on free availability; paywalled-abstract articles are excluded.
- Volume: ~85 folder + discovered articles × 2–3 MCQs ≈ 250–400 MCQs. May parallelize generation with subagents; catalog keeps it consistent.
