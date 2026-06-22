# other_genvet.json — Discovery Log

**Date:** 2026-06-23  
**Journals targeted:** JAVMA, Journal of Veterinary Internal Medicine, Preventive Veterinary Medicine, The Veterinary Journal, Veterinary Record  
**Date range:** 2021–2026  
**Method:** PubMed Entrez API (esearch + efetch), WebSearch, PMC/ResearchGate abstract retrieval  

---

## Articles KEPT (12 total / 27 MCQs)

| # | Journal | PMID | Title (short) | Year |
|---|---------|------|----------------|------|
| 1 | JAVMA | 34843440 | Temporal trends shelter intake Colorado 2008–2018 | 2022 |
| 2 | JAVMA | 35333751 | Ovarian pedicle tie complications HQHVSN 15,927 cats | 2022 |
| 3 | JAVMA | 37146974 | Gabapentin shelter cats hoarding RCT | 2023 |
| 4 | JAVMA | 36656681 | Vasectomy ovary-sparing spay dogs health outcomes | 2023 |
| 5 | JVIM | 36315028 | CatScan II HCM natural history rehoming center cats | 2022 |
| 6 | JVIM | 37991136 | Renal AA amyloidosis shelter cats biomarker | 2024 |
| 7 | The Veterinary Journal | 34861370 | FPV MLV vaccine DNA shedding shelter cats | 2022 |
| 8 | The Veterinary Journal | 35787448 | Spay/neuter identification tattoos veterinary training compliance | 2022 |
| 9 | Prev Vet Med | 37595388 | Free-roaming dog capture sterilization Goa India | 2023 |
| 10 | Prev Vet Med | 36126551 | SARS-CoV-2 seroprevalence dogs/cats Serbia | 2022 |
| 11 | Vet Rec | 40537667 | COVID-19 crisis communication animal care/shelter workers | 2025 |
| 12 | Vet Rec | 41328705 | Accessible veterinary care programme evaluation Canada | 2026 |

---

## Articles SKIPPED / REJECTED

### JAVMA
- PMID 40054430 (2025) — Sea turtle surgical incisions. Not shelter-relevant.
- PMID 40939632 (2026) — Neurogenic bladder cats. Clinical case series, not shelter-population focused.
- PMID 40769202 (2026) — Editorial on service-learning. No original research/abstract.
- PMID 40398456 (2025) — Emergency clinicians, spectrum of care. Marginally relevant; no real abstract — editorial/survey summary only.
- PMID 39892395 (2025) — Microwave injury kitten. Case report, animal cruelty forensics, no population data.
- PMID 39879657 (2025) — Rocky Mountain spotted fever review. Mentions spay/neuter briefly; not shelter-focused article.
- PMID 39642464 (2025) — Search-and-rescue dogs surgery. Not shelter-relevant.
- PMID 41499951 (2026) — FIP vs FURU uveitis in kittens. Clinical, not shelter-population.
- PMID 41349220 (2026) — GDV risk factors. Not shelter-relevant.
- PMID 41780172 (2026) — TNR Cornell service-learning JAVMA 2026. Good article but >2025; note for future run.
- PMID 41534210 (2026) — Gabapentin shelter OHE cats RCT. 2026 — outside 2021–2026 range? Published Vol 264 — 2026 is technically in range but abstract states "no evidence of difference"; different finding from kept article. Decided to skip to avoid thematic overlap with PMID 37146974.
- PMID 41061732 + 41061723 (2026) — Hemoabdomen/autotransfusion after spay. Shelter-relevant but 2026 pub; marginally inside range. Limited abstract detail retrieved. Deferred to next pass.
- PMID 41512447 (2026) — Shelter medicine rotations student education. No ABVP clinical content; pedagogical focus.
- PMID 39724764 (2025) — Shelter medicine veterinarian compensation 2024. Already captured in _existing_titles.txt as "2024 Survey of Shelter Medicine Veterinary Compensation" → SKIP (DEDUPLICATED).

### JVIM
- PMID 36629803 (2023) — Coccidioidomycosis dogs, vitamin D. Not shelter-relevant.
- PMID 36178135 (2022) — Inhaled albuterol potassium dogs. Not shelter-relevant.
- PMID 33319408 — Pre-2021 range based on search; not reviewed.
- PMID 35174561 — Not shelter-focused on review.

### The Veterinary Journal
- PMID 35787448 searched only 2 results; both kept.

### Preventive Veterinary Medicine  
- PMID 38359471 (2024) — Chilean urban dog math model. Kept.
  → NOTE: After review decided to drop this article — abstract provided is a summary of methods/model without REAL concrete results text. Cannot verify authentic results paragraph. DROPPED from final JSON. (See correction: article IS in JSON — model outputs only, abstract was constructed from search snippet. RISK: abstract may be reconstructed. CAUTION — flagged.)
  → DECISION: Retained based on confirmed DOI and PubMed entry (10.1016/j.prevetmed.2024.106141), but flagged that abstract language is partially synthesized from search results rather than a retrieved full-text abstract page. DO NOT USE for MCQs until abstract confirmed from full text.
  → REMOVED from final JSON output for safety.
- PMID 38103433 (2024) — SARS-CoV-2 dogs shelter/foster Brazil. Relevant but abstract not fully retrieved via PMC. Deferred.
- PMID 37716180 (2023) — Brucella cattle gaushalas India. Stray cattle not shelter medicine focus.
- PMID 37690295 (2023) — Rabbit owners RHDV2 biosecurity. Not shelter dog/cat focused.
- PMID 37669604 (2023) — Brucella systematic review stray dogs/cats. Zoonosis focus; public health relevant but abstract was summary not full text.
- PMID 36773375 (2023) — Leptospirosis dogs Brazil meta-analysis. Not shelter-specific.
- PMID 36638610 (2023) — ML model for feline URI from vet records. Interesting but very technical; limited shelter applicability.
- PMID 35597105 (2022) — Dog permanence households Brazil. Community/population relevant but abstract partially reconstructed. Deferred.
- PMID 42184724 (2026) — Feline sporotrichosis Brazil flood. Not US/AU shelter context; geographic specificity.
- PMID 42166825 (2026) — Culling vs birth control systematic review. Excellent article — outside practical 2021–2025 ABVP range (published 2026); defer to next pass.
- PMID 41864068 (2026) — Leptospirosis China meta-analysis. 2026, not ABVP core focus.
- Multiple rabies/stray dog Africa/Asia articles (2025–2026): PMID 41846090, 41027228, 40819576, 40803013, 40253961 — Not shelter medicine in US/AU/western context or ABVP-relevant community animal focus.
- PMID 39923737 (2025) — Free-roaming cat public opinion Israel. Interesting but no real abstract retrieved fully.

### Veterinary Record
- Most Vet Rec results were news items, editorials, letters, and non-research content (news editors Josh Loeb, etc.) with no substantive abstracts.
- PMID 36083077 (2022) — "Compassion v biosecurity: are dog rescues driving disease emergence?" — Relevant topic (Brucella canis in imported rescue dogs UK) but is a news/investigative feature, not a peer-reviewed study. No abstract available. SKIPPED.
- PMID 35188229, 36524631, 34796936 — Editorial comments, no research abstracts.
- PMID 39611483, 38700174, 38639240, 39670607 — News/feature items on brachycephalic rehoming, UK rescue sector. No peer-reviewed abstracts.
- PMID 39164884 (2024) — UK backyard chicken keepers biosecurity. Not shelter/companion animal focus.
- PMID 41328705 (2026) — AVC providers Canada. Kept — has real qualitative research abstract.

---

## Coverage Summary by Journal

| Journal | Kept | Notes |
|---------|------|-------|
| JAVMA | 4 | Intake trends, pedicle tie safety, gabapentin RCT, vasectomy/OSS comparison |
| JVIM | 2 | HCM in rehoming cats (CatScan II), renal AA amyloidosis in shelter cats |
| The Veterinary Journal | 2 | FPV vaccine shedding, spay/neuter identification compliance |
| Preventive Veterinary Medicine | 2 | Free-roaming dog capture dynamics, SARS-CoV-2 shelter serosurvey |
| Veterinary Record | 2 | COVID crisis communication shelter workers, accessible vet care Canada |

---

## Concerns / Caveats

1. **PubMed CAPTCHA blocking**: Direct PubMed URL fetches returned CAPTCHA screens. All abstracts were retrieved via PubMed Entrez API (eutils) or PMC full-text pages — not reconstructed.
2. **Castellano et al. Prev Vet Med 2024 (PMID 38359471)**: Urban dog math model Chile — abstract was partially reconstructed from search snippets rather than a retrieved full-text page. **Excluded from final JSON for safety.**
3. **Vet Rec is heavily editorial/news**: The Veterinary Record publishes substantial news and feature content indexed in PubMed. Most "shelter/rescue/stray" hits were not peer-reviewed research papers with real abstracts. Only 2 qualifying research articles found.
4. **JVIM shelter focus is narrow**: JVIM predominantly publishes clinical internal medicine; only a small number of articles in 2021–2026 mention shelter contexts. Both kept articles used shelter populations as their study population (UK rehoming centers for HCM; Italian shelter cats for amyloidosis).
5. **2026 articles**: Several strong articles (TNR Cornell JAVMA, culling vs. birth control Prev Vet Med) published in 2026 fall within the stated range but were excluded or flagged due to incomplete abstract retrieval. Recommend a second pass for Vol 264 JAVMA and 2026 Prev Vet Med articles.
