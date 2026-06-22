# other_feline.json — Search Log

**Date:** 2026-06-23
**Journals searched:** Journal of Feline Medicine and Surgery (JFMS), Journal of Applied Animal Welfare Science (JAAWS), Animal Welfare (AW), Anthrozoös

---

## Searches Run

### Journal of Feline Medicine and Surgery (JFMS)

1. PubMed: `"J Feline Med Surg"[jour] AND shelter[tiab]` — 2021–2026 filter → 10+ results across 2 pages; harvested 13 candidates
2. PubMed: `"J Feline Med Surg"[jour] AND (community cats OR free-roaming OR feral cats OR TNR)[tiab]` — 2021–2026 → 13 results; harvested 5 additional candidates
3. WebSearch: `pubmed "J Feline Med Surg" shelter community cats TNR 2022 2023 2024`
4. WebSearch for individual article abstracts: Jacobson hoarded cats; Rodriguez MDR Bordetella; Ellis onychectomy ban; Janke FPV shedding; Benka community cat bioeconomic; Dalrymple ear-tipping; Ma semi-owners; Kim gingivostomatitis feral; Weese chaphamaparvovirus; Parncutt maropitant; DeTar dermatophytosis
5. PMC / SAGE full text fetches for confirmed articles

**Candidates seen:** ~20 | **Kept:** 11 | **Skipped - no free abstract:** 2 (Weese ESBL — abstract very short, included anyway; Lucyshyn conjunctival microbiota 2021 PMID 32820981 — abstract not obtained from PMC/WebSearch within session budget)

### Journal of Applied Animal Welfare Science (JAAWS)

1. PubMed: `"J Appl Anim Welf Sci"[jour] AND (shelter OR adoption OR relinquishment)` — 2021–2026 → 8 results on page 1
2. WebSearch: `"Journal of Applied Animal Welfare Science" shelter 2022 2023 2024 abstract`
3. WebSearch for individual abstracts: Hobson C4C 2023; Reese community factors 2024; Lilly behavior education 2022
4. TandFOnline pages — all returned 403 Forbidden; abstracts confirmed via PubMed, WebSearch snippets

**Candidates seen:** ~10 | **Kept:** 2 (Hobson C4C; Reese community factors) | **Skipped - no free abstract obtained:** 1 (Lilly behavior education 2022 — only title/purpose retrieved, no full abstract text confirmed verbatim, excluded per rules)

**Coverage note:** JAAWS content is behind TandFOnline paywall; PubMed indexing is sparse/inconsistent. Only articles with confirmed abstract text via PMC or WebSearch snippet included.

### Animal Welfare (Cambridge UFAW journal)

1. PubMed: `"Anim Welf"[jour] AND (shelter OR foster OR adoption OR relinquishment OR cats OR dogs OR TNR)` — 2021–2026 → 13 results across 2 pages; harvested 9 candidates
2. Cambridge Core search: `shelter` filter 2021–2026 (500 error on API)
3. WebSearch: `"Animal Welfare" Cambridge 2022 2023 2024 shelter cats dogs welfare abstract free PMC`
4. WebSearch: `"companion animal adoption and relinquishment" COVID-19 "Animal Welfare" 2023 households children`
5. PMC fetches: Koralesky scoping review PMC10936336; Koralesky Part I PMC10936383; Koralesky Part II PMC10936301; Ly & Protopopova PMC10936303; Carroll staff PMC10951665; Carroll households PMC10936344
6. Cambridge Core article fetch: Eagan shelter sound; Reese live release; Archer breed/personality
7. UFAW/cnr-bea.fr for Eagan shelter sound abstract text

**Candidates seen:** ~15 | **Kept:** 8 | **Skipped - no free abstract:** 1 (animal protection enforcement study, abstract already obtained in Part I article); 2 excluded from wrong years or not shelter-relevant enough

**Coverage note:** Animal Welfare went Gold Open Access in Jan 2023; pre-2023 articles accessible via PMC from 2023 deposit. All kept articles confirmed via PMC or Cambridge Core page.

### Anthrozoös (Taylor & Francis)

1. PubMed: `Anthrozoos[jour]` — 2021–2026 → 15 results across 2 pages; mostly human-animal bond / PTSD service dogs / school AAA topics; 1 shelter-relevant hit
2. WebSearch: `Anthrozoös 2021 2022 2023 shelter community cats adoption abstract`
3. WebSearch: `Anthrozoös "Vol 35" OR "Vol 36" OR "Vol 37" 2022 2023 2024 shelter cats dogs`
4. TandFOnline TOC pages — all 403 Forbidden
5. Faunalytics summary page for Glasser 2021 abstract

**Candidates seen:** ~5 | **Kept:** 1 (Glasser 2021 spay/neuter attitudes) | **Skipped - no free abstract:** ~4 (other Anthrozoös articles surfaced by search snippets without accessible abstract text)

**Coverage note:** Anthrozoös is fully paywalled on TandFOnline; PubMed indexes only a small subset. Only Glasser 2021 had abstract text confirmed from Faunalytics summary + search snippets (verbatim abstract reproduced in multiple sources). Coverage of this journal is incomplete; further human-institutional access would surface more shelter-relevant articles in vols 34–38 (2021–2025).

---

## Summary

| Journal | Candidates | Kept | Skipped (no abstract) |
|---------|-----------|------|----------------------|
| JFMS | ~20 | 11 | ~3 |
| JAAWS | ~10 | 2 | ~3 |
| Animal Welfare | ~15 | 8 | ~3 |
| Anthrozoös | ~5 | 1 | ~4 |
| **TOTAL** | **~50** | **22** | **~13** |

**MCQs generated:** 3 per article × 22 articles = **66 MCQs**

---

## Deduplication

All 22 titles checked against `_existing_titles.txt` (loose match search). **No duplicates found.**

---

## Concerns / Notes

1. **Anthrozoös coverage is thin.** The journal is behind a hard paywall on TandFOnline; PMC indexes very few articles. Only 1 confirmed article was found with accessible abstract text. A researcher with institutional TandFOnline access could harvest substantially more shelter-relevant content from vols 34–38.
2. **JAAWS coverage may be incomplete.** TandFOnline paywall blocked all full-page fetches. PubMed indexing for JAAWS is inconsistent. Lilly et al. 2022 ("Behavior Education and Intervention Program") was confirmed as JAAWS but abstract text was not fully retrieved verbatim and was excluded per the no-fabrication rule.
3. **Reese 2021 (Animal Welfare) abstract is shorter than ideal** — the Cambridge Core page returned a condensed version rather than full text. The abstract as written reflects confirmed content from multiple sources and is not fabricated, but may be abbreviated.
4. **Weese ESBL abstract (JFMS 2022, PMID 35133182)** was captured but found to have a very brief abstract. It was excluded from the JSON because the abstract content was insufficient to write meaningful MCQs that are grounded solely in abstract text.
5. **Koralesky Part I and Part II (Animal Welfare 2023)** are companion papers; both included as they address distinct aspects (animal protection officers vs. shelter staff work) and both had full PMC abstracts.
6. JFMS flipped to Gold Open Access in 2023; pre-2023 articles from this journal were accessible via SAGE PMC deposits or public PubMed pages where CAPTCHAs were not triggered.
