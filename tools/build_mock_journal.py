#!/usr/bin/env python3
"""Add journal-derived MCQs to the mock exam pool.

Writes mock-data-journal.js (appends to window.MOCK.mcqs) and ensures
mock-exam.html loads it after mock-data.js. Idempotent.
"""
import os, sys, json, re, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from lib_catalog import load_catalog

CATALOG = os.path.join(HERE, "journal-catalog.json")
SYNTH = os.path.join(HERE, "synthesized_mcqs.json")
OUT_JS = os.path.join(ROOT, "mock-data-journal.js")
MOCK_HTML = os.path.join(ROOT, "mock-exam.html")

FOLDER_DOMAIN = {
    "physical-health": "Physical Health",
    "shelter-management": "Shelter Management",
    "behavioral-health": "Behavioral Health",
    "companion-animal-homelessness": "Companion Animal Homelessness",
    "community-public-health": "Community & Public Health",
    "animals-public-policy": "Animals & Public Policy",
    "research-biostats": "Research & Biostats",
}

PAGE_SUB = {
    "physical-health/infectious_disease_hub.html": "Infectious Disease",
    "physical-health/sanitation_biosecurity_hub.html": "Sanitation & Biosecurity",
    "physical-health/surgery_anesthesia_hub.html": "Surgery & Anesthesia",
    "physical-health/vaccination_hub.html": "Vaccination",
    "physical-health/facility_shelter_design_hub.html": "Facility/Environment",
    "physical-health/euthanasia_hub.html": "Euthanasia",
    "physical-health/medical_health_hub.html": "Medical (Non-Infectious)",
    "physical-health/nutrition_husbandry_hub.html": "Nutrition & Husbandry",
    "physical-health/parasites_hub.html": "Parasites",
    "physical-health/other-animals_hub.html": "Medical (Non-Infectious)",
    "shelter-management/01_population_management.html": "Population Management",
    "shelter-management/02_animal_id_tracking.html": "Animal ID & Stats",
    "shelter-management/03_management_leadership.html": "Management & Leadership",
    "shelter-management/04_record_keeping.html": "Record Keeping",
    "shelter-management/05_data_analysis.html": "Data & Analysis",
    "shelter-management/06_mental_health.html": "Mental Health & Self-Care",
    "shelter-management/07_regulatory.html": "Regulatory",
    "shelter-management/08_liability.html": "Liability",
    "shelter-management/09_resource_allocation.html": "Resource Allocation",
    "behavioral-health/01_qol_needs_assessment.html": "QOL & Needs Assessment",
    "behavioral-health/02_animal_handling.html": "Animal Handling",
    "behavioral-health/03_assessment_decision_making.html": "Assessment & Decision",
    "behavioral-health/04_body_language.html": "Body Language",
    "behavioral-health/05_common_behaviour_problems.html": "Common Behavior Problems",
    "behavioral-health/06_stress.html": "Stress",
    "behavioral-health/07_facility_environment.html": "Facility/Environment",
    "behavioral-health/08_learning_theory.html": "Learning Theory",
    "behavioral-health/09_behaviour_medications.html": "General",
    "behavioral-health/10_behaviour_relinquishment.html": "General",
    "behavioral-health/12_fear_phobias_anxiety.html": "General",
    "behavioral-health/13_shelter_animal_enrichment.html": "General",
    "behavioral-health/14_training_bmod_playgroups.html": "General",
    "community-public-health/01_animal_cruelty.html": "Animal Cruelty",
    "community-public-health/01e_hoarding.html": "Animal Cruelty",
    "community-public-health/02_zoonotic_disease.html": "Zoonotic Disease",
    "community-public-health/03_animals_public_safety.html": "Animals & Public Safety",
    "community-public-health/04_rabies.html": "Rabies",
    "community-public-health/05_reportable_emerging.html": "Reportable & Emerging",
    "companion-animal-homelessness/access_vet_care_hub.html": "Epidemiology of Homelessness",
    "companion-animal-homelessness/adoption_placement_hub.html": "Adoption & Placement",
    "companion-animal-homelessness/animal_transport_relocation_hub.html": "Transfer Programs",
    "companion-animal-homelessness/disaster_emergency_hub.html": "Disaster",
    "companion-animal-homelessness/nonsurgical_sterilization_hub.html": "Non-Surgical Sterilization",
    "companion-animal-homelessness/shelter_diversion_hub.html": "Shelter Diversion",
    "companion-animal-homelessness/spay_neuter_hub_2.html": "Spay-Neuter",
    "animals-public-policy/01_ethics_animal_welfare.html": "Ethics",
    "animals-public-policy/02_regulatory.html": "Regulatory",
    "animals-public-policy/03_legislation.html": "Legislation",
    "animals-public-policy/04_animal_shelter_history.html": "Animal Shelter History",
    "research-biostats/epidemiology_biostats_hub.html": "Epidemiology & Biostats",
    "research-biostats/study_design_hub.html": "Study Design",
}


def dom_sub(page):
    folder = page.split("/")[0]
    return FOLDER_DOMAIN.get(folder, "General"), PAGE_SUB.get(page, "General")


def main():
    cat = load_catalog(CATALOG)
    synth = json.loads(open(SYNTH, encoding="utf-8").read()) if os.path.exists(SYNTH) else []

    mocks = []
    for r in cat:
        dom, sub = dom_sub(r["subdomain_page"])
        for m in r.get("mcqs", []):
            mocks.append({"type": "mcq", "domain": dom, "sub": sub,
                          "q": m["q"], "o": m["o"], "a": m["a"], "e": m["e"], "source": "journal"})
    for s in synth:
        dom, sub = dom_sub(s.get("subdomain_page", ""))
        mocks.append({"type": "mcq", "domain": dom, "sub": sub,
                      "q": s["q"], "o": s["o"], "a": s["a"], "e": s["e"], "source": "journal"})

    # Carry over any question already in the output that the catalog can no
    # longer produce. mock-data-journal.js has drifted ahead of the catalog:
    # 29 MCQs (parasites, infectious disease, nutrition, euthanasia, …) live
    # only in the generated file, with no backing article in
    # journal-catalog.json or synthesized_mcqs.json and no field identifying
    # where they came from. A plain overwrite deletes them silently, which is
    # how a routine rebuild quietly drops real content. Preserve them and say
    # so; pass --prune to drop them deliberately once they are back-filled.
    orphans = []
    if os.path.exists(OUT_JS) and "--prune" not in sys.argv:
        try:
            prev_raw = re.search(r"var J=(\[.*\]);", open(OUT_JS, encoding="utf-8").read(), re.S)
            prev = json.loads(prev_raw.group(1)) if prev_raw else []
            fresh = {m["q"] for m in mocks}
            candidates = [m for m in prev if m.get("q") not in fresh]
            # An unmatched question that is a near-duplicate of one the catalog
            # *does* produce is a superseded variant, not lost content — e.g.
            # the pre-dual-unit wording of a stem that now reads "-80 degrees C
            # (-112°F)". Preserving those would re-add the stale copy on every
            # run and slowly accumulate duplicate questions in the mock exam.
            by_prefix = {}
            for m in mocks:
                by_prefix.setdefault(m["q"][:40], []).append(m["q"])
            orphans, superseded = [], 0
            for m in candidates:
                near = [
                    q for q in by_prefix.get(m["q"][:40], [])
                    if difflib.SequenceMatcher(None, m["q"], q).ratio() >= 0.90
                ]
                if near:
                    superseded += 1
                else:
                    orphans.append(m)
            if superseded:
                print(f"  - dropped {superseded} superseded variant(s) the catalog now supplies")
        except Exception as exc:                     # unreadable/absent → nothing to keep
            print(f"  ! could not read existing {os.path.basename(OUT_JS)}: {exc}")
    if orphans:
        by_sub = {}
        for m in orphans:
            by_sub[m.get("sub", "?")] = by_sub.get(m.get("sub", "?"), 0) + 1
        print(f"  ! preserving {len(orphans)} MCQ(s) with no catalog entry: "
              + ", ".join(f"{k} x{v}" for k, v in sorted(by_sub.items())))
        print("    (back-fill these into journal-catalog.json, then rerun with --prune)")
        mocks.extend(orphans)

    payload = json.dumps(mocks, ensure_ascii=False, indent=0)
    js = ("/* Auto-generated journal MCQs for the mock exam. Loaded after mock-data.js. */\n"
          "(function(){\n"
          "  if(!window.MOCK){window.MOCK={mcqs:[]};}\n"
          "  if(!window.MOCK.mcqs){window.MOCK.mcqs=[];}\n"
          "  var J=" + payload + ";\n"
          "  window.MOCK.mcqs=window.MOCK.mcqs.concat(J);\n"
          "})();\n")
    open(OUT_JS, "w", encoding="utf-8").write(js)

    # Ensure mock-exam.html loads it right after mock-data.js (idempotent)
    html = open(MOCK_HTML, encoding="utf-8").read()
    inc = '<script src="mock-data-journal.js"></script>'
    if inc not in html:
        html = html.replace('<script src="mock-data.js"></script>',
                            '<script src="mock-data.js"></script>\n' + inc, 1)
        open(MOCK_HTML, "w", encoding="utf-8").write(html)
        added = True
    else:
        added = False

    by_dom = {}
    for m in mocks:
        by_dom[m["domain"]] = by_dom.get(m["domain"], 0) + 1
    print(f"wrote {OUT_JS} with {len(mocks)} journal MCQs")
    print("by domain:", json.dumps(by_dom, ensure_ascii=False))
    print("mock-exam.html include:", "added" if added else "already present")


if __name__ == "__main__":
    main()
