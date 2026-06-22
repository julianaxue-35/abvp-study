#!/usr/bin/env python3
"""
extract_folder.py — ABVP Journal Catalog: Extract abstracts from folder PDFs.

For each .pdf in SOURCE_DIR:
  1. Derives title from filename (strips [Abstract], suffix, normalises whitespace).
  2. Runs pdftotext -layout, extracts abstract text.
  3. Extracts year, authors, journal, doi.
  4. Builds a citation string.
  5. Maps to subdomain via keyword rules.
  6. Saves all valid records to tools/journal-catalog.json via save_catalog.
  7. Writes tools/extract_report.md with per-file results.

Usage:
    export PATH="/opt/homebrew/bin:$PATH"
    python3 tools/extract_folder.py
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Ensure tools/ is on the path so we can import lib_catalog
TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

import lib_catalog  # noqa: E402 (placed after sys.path modification)

SOURCE_DIR = Path(
    "/Users/jxue/Library/CloudStorage/Dropbox/work docs/"
    "ABVP specialist pathway/reading list/journal article"
)
CATALOG_PATH = str(TOOLS_DIR / "journal-catalog.json")
REPORT_PATH = str(TOOLS_DIR / "extract_report.md")

# ---------------------------------------------------------------------------
# Subdomain mapping rules
# Each entry: (list_of_regex_patterns, page_path, domain_name)
# First match wins — ORDER MATTERS (most specific / highest priority first).
#
# Strategy:
#   1. Highly specific identifiers first (disease names, unique terms)
#   2. Community cats / TNR BEFORE surgery (many TNR papers mention spay/neuter)
#   3. Vaccination BEFORE surgery (rabies vaccine papers go to vaccination)
#   4. Access-to-care BEFORE adoption/surgery (pyometra, barriers papers)
#   5. Hoarding BEFORE cruelty
#   6. Ethics committee BEFORE euthanasia
#   7. Surgery is broad but only fires after everything more specific
# ---------------------------------------------------------------------------
DOMAIN_RULES = [
    # =========================================================================
    # HIGH-SPECIFICITY RULES — unique terms that cannot be confused
    # =========================================================================

    # --- Physical Health: Parasites (very specific terms) ---
    (
        [
            r"intestinal.?parasit|GI.?parasit|gastrointestinal.{0,20}parasit",
            r"heartworm",
            r"giardia",
            r"helminth|hookworm|roundworm|whipworm|Toxocara|Ancylostoma",
        ],
        "physical-health/parasites_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Other Animals (RHDV, rabbits) ---
    (
        [
            r"rabbit|RHDV|Oryctolagus",
            r"small.?mammal|guinea.?pig|hamster|ferret",
        ],
        "physical-health/other-animals_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Facility & Shelter Design (cat dens - MUST be BEFORE infectious disease) ---
    # "The Inclusion of Cat Dens" title has "upper respiratory infection" in the same title;
    # placing this block first ensures cat-den papers route to facility design, not infectious disease.
    (
        [
            r"cat.?dens?\b",
            r"inclusion.{0,20}cat.{0,20}den",
            r"cat.?den.{0,30}(?:upper.?respir|URI|shelter|population|LOS|length.of.stay)",
        ],
        "physical-health/facility_shelter_design_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Medical Health (Burkholderia must precede infectious disease) ---
    (
        [
            r"Burkholderia",
            r"low.cost.{0,20}veterinary.{0,20}clinical.{0,20}diagnos",
            r"postmortem|morbidity.{0,20}mortality.{0,20}review|mortality.{0,20}morbidity",
            r"Good.Samaritan.{0,30}animal|tertiary.?referral.{0,30}health",
        ],
        "physical-health/medical_health_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Infectious Disease (specific pathogens) ---
    (
        [
            r"parvovirus|parvo\b",
            r"panleukopenia|panleucop|panleuk",
            r"upper.?respiratory.{0,30}(?:infection|disease|tract|tract.disease)",
            r"URI.{0,15}(?:incidence|disease|infection|diagnos|treat|rate|prevention)",
            r"CIRDC\b",
            r"calicivirus|calici\b(?!um)",
            r"bordetella",
            r"ringworm|dermatophyte|Microsporum|Trichophyton",
            r"\bFeLV\b|retrovirus.{0,20}cat",
            r"SARS.CoV.?2|SARS.CoV\b",
            r"COVID.19|coronavirus.{0,20}(?:shelter|cat|dog)",
            r"H7N2\b",
            r"monoclonal.?antibody|CPMA\b",
            r"wastewater.{0,30}pathogen|pathogen.{0,30}wastewater",
        ],
        "physical-health/infectious_disease_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Sanitation & Biosecurity ---
    (
        [
            r"disinfect|biosecurity.?framework",
            r"HPAI.{0,30}biosecurity|biosecurity.{0,30}HPAI",
            r"HPAI.{0,30}mitig|mitig.{0,30}HPAI",
        ],
        "physical-health/sanitation_biosecurity_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Nutrition & Husbandry ---
    (
        [
            r"nutrition|feeding|body.?condition",
            r"weight.{0,20}estimat|estimat.{0,20}weight",
            r"elderly.{0,15}cat.{0,30}nutrition|nutrition.{0,30}elderly.{0,15}cat",
            r"senior.{0,15}cat|campus.{0,20}cat.{0,20}nutrition|nutritional.{0,20}management",
        ],
        "physical-health/nutrition_husbandry_hub.html",
        "Physical Health of Animal",
    ),
    # --- Physical Health: Vaccination ---
    # Note: must come BEFORE surgery so "rabies vaccine" goes here, not surgery
    (
        [
            r"vaccine.?vial|vial.?septa|needle.{0,20}vaccine",
            r"MLV.?distemper|modified.?live.{0,20}distemper",
            r"rabies.{0,30}vaccin|vaccin.{0,30}rabies",
            r"vaccin.{0,30}antibody.{0,30}response|antibody.{0,30}vaccin",
            r"perioperative.{0,20}rabies|rabies.{0,20}perioperative",
            r"response.{0,20}rabies.{0,20}vaccine|rabies.{0,20}vaccine.{0,20}kitten",
        ],
        "physical-health/vaccination_hub.html",
        "Physical Health of Animal",
    ),
    # =========================================================================
    # BREED-SPECIFIC LEGISLATION (shelter-management regulatory outcomes)
    # Placed BEFORE access-to-care to catch BSL articles that mention "care"
    # =========================================================================
    (
        [
            r"breed.?specific.?legislation",
            r"canine.{0,30}outcomes?.{0,30}(?:breed|BSL|ordinance)|(?:breed|BSL).{0,30}canine.{0,30}outcomes?",
            r"ordinance.{0,30}(?:canine|dog).{0,30}outcomes?|(?:canine|dog).{0,30}outcomes?.{0,30}ordinance",
            r"BSL.{0,20}shelter|shelter.{0,20}BSL",
        ],
        "shelter-management/07_regulatory.html",
        "Shelter Management",
    ),
    # =========================================================================
    # ACCESS TO VET CARE — before adoption and surgery
    # =========================================================================
    (
        [
            r"access.{0,30}veterinary.?care|veterinary.?care.{0,30}(?:access|desert|barrier|need)",
            r"vet.?care.?desert|nonprofit.{0,20}veterinarian|veterinarian.{0,20}shortage",
            r"barriers?.{0,30}(?:veterinary|vet).?care|(?:veterinary|vet).?care.{0,30}barriers?",
            r"barriers?.{0,30}lack.{0,30}access|lack.{0,30}access.{0,30}veterinary",
            r"telemedicine.{0,30}(?:access|care|welfare|animal.?welfare)",
            r"Latino.{0,30}veterinary|Hispanic.{0,30}veterinary|veterinary.{0,30}Latino|veterinary.{0,30}Hispanic",
            r"Knoxville.{0,30}(?:Latino|Hispanic)|(?:Latino|Hispanic).{0,30}Knoxville",
            r"AVCC.{0,20}priority|twenty.{0,20}highest.{0,20}priority|highest.{0,20}priority.{0,20}question",
            r"pyometra",
            r"vet.{0,20}care.{0,30}(?:Canada|desert|needs)",
            r"nonprofit.{0,20}vet|who.{0,20}will.{0,20}care.{0,20}for.{0,20}the.{0,20}pets",
            r"veterinarian.{0,20}shortage.{0,20}who.{0,20}will",
            r"dog.{0,20}acquisition.{0,20}(?:lower.income|low.income)|lower.income.{0,20}(?:dog|pet).{0,20}acqui",
            r"acqui.{0,30}(?:dog|pet).{0,20}low.income|low.income.{0,30}acqui.{0,30}(?:dog|pet)",
        ],
        "companion-animal-homelessness/access_vet_care_hub.html",
        "Companion Animal Homelessness",
    ),
    # =========================================================================
    # COMMUNITY CATS / TNR / SPAY-NEUTER PROGRAMS
    # Must come BEFORE surgery and vaccination rules to avoid false matches
    # =========================================================================
    (
        [
            r"TNR\b|trap.neuter.return|trap-neuter-return",
            r"community\s+cats?\b|free.?roaming\s+cats?\b|feral\s+cats?\b",
            r"return.to.field\b",
            r"working.?cat.?program",
            r"spaycation",
            r"remote.{0,20}volunteer.{0,20}spay|volunteer.{0,20}spay.{0,20}neuter",
            r"feral.{0,20}cat.{0,20}coloni|coloni.{0,20}feral.{0,20}cat",
            r"unowned.?cat",
            r"cat.{0,20}population.{0,20}(?:management|dynamic|control)",
            r"managing.{0,20}cat.{0,20}population|managing.{0,20}free.{0,20}roaming",
            r"cat.{0,20}lifestyle.{0,20}and.{0,20}population|cat.{0,20}population.{0,20}based",
            r"sterilized.{0,20}(?:dogs|cats).{0,20}entering|proportion.{0,20}sterilized",
            r"decrease.{0,20}(?:proportion|sterilized)|sterilization.{0,20}status.{0,20}(?:dog|entering)",
            r"outcom.{0,20}kittens.{0,20}born.{0,20}(?:to\s+)?free.?roaming",
            r"who\s+cares.{0,40}community|community\s+cat.{0,20}caregiver|providing.{0,20}care.{0,20}community\s+cat",
            r"attachment.{0,20}community\s+cat|community\s+cat.{0,20}(?:attachment|transcend|ownership)",
            r"cat.{0,20}(?:is.{0,5}a.{0,5}cat)|ownership.{0,10}status.{0,10}community",
            r"Slovakia.{0,20}(?:cat|unowned)|cat.{0,20}Slovakia",
            r"AirTag.{0,20}feral|feral.{0,20}AirTag|home.{0,20}range.{0,20}feral",
            r"HQHVSN.{0,20}(?:clinic|remote|spaycation|veterinarian)",
            r"HPAI.{0,20}free.?roaming|free.?roaming.{0,20}HPAI",
            r"inconvenient.{0,20}truth.{0,20}(?:TNR|targeted)|targeted.{0,20}TNR",
            r"lethal.{0,20}method.{0,20}(?:managing|free.?roaming|cat)",
            r"cat.{0,20}principles.{0,20}(?:working|unowned)|principles.{0,20}(?:unowned.{0,20})?cat",
        ],
        "companion-animal-homelessness/spay_neuter_hub_2.html",
        "Companion Animal Homelessness",
    ),
    # =========================================================================
    # ANIMAL ID & TRACKING — ear tipping (for ID), AirTags (for pet cats), microchips
    # Note: Ear tipping of COMMUNITY CATS goes to spay_neuter_hub_2 (handled above);
    #       here we catch ear tipping as an identification method in general.
    # =========================================================================
    (
        [
            r"ear.?tip(?:ping)?.{0,30}(?:identify|identification|ID|technique|method|comparison)",
            r"AirTag.{0,30}(?:pet|owned|home.{0,5}range.{0,20}(?:pet|owned))",
            r"microchip",
            r"tag.{0,15}you.{0,10}re.{0,10}home.{0,20}(?:reunif|cat|pet)",
            r"reunif.{0,20}(?:pet|cat).{0,20}(?:owner|community.{0,20}engag)",
        ],
        "shelter-management/02_animal_id_tracking.html",
        "Shelter Management",
    ),
    # =========================================================================
    # HOARDING — before cruelty (hoarding papers often mention welfare/cruelty)
    # =========================================================================
    (
        [r"hoard"],
        "community-public-health/01e_hoarding.html",
        "Community and Public Health",
    ),
    # =========================================================================
    # ETHICS COMMITTEE — before euthanasia
    # =========================================================================
    (
        [
            r"ethics.?committee",
            r"animal.?welfare.?philosophy|welfare.?philosophy",
        ],
        "animals-public-policy/01_ethics_animal_welfare.html",
        "Animals and Public Policy",
    ),
    # =========================================================================
    # PHYSICAL HEALTH: Euthanasia
    # =========================================================================
    (
        [
            r"euthanasia|euthaniz",
            r"end.of.life",
        ],
        "physical-health/euthanasia_hub.html",
        "Physical Health of Animal",
    ),
    # =========================================================================
    # PHYSICAL HEALTH: Infectious Disease (broader — influenza, HPAI, distemper,
    # outbreak — placed after biosecurity so HPAI biosecurity goes there)
    # =========================================================================
    (
        [
            r"distemper",
            r"outbreak\b",
            r"influenza|HPAI\b|H7N2",
        ],
        "physical-health/infectious_disease_hub.html",
        "Physical Health of Animal",
    ),
    # =========================================================================
    # SHELTER MANAGEMENT
    # =========================================================================
    # --- Population Management ---
    (
        [
            r"length.?of.?stay.{0,50}driver|driver.{0,50}length.?of.?stay",
            r"foster.?based.{0,20}kitten|kitten.{0,20}foster.?based|kitten.{0,20}rearing.{0,20}model",
            r"deferred.?intake",
            r"capacity.?for.?care",
        ],
        "shelter-management/01_population_management.html",
        "Shelter Management",
    ),
    # --- Leadership ---
    (
        [
            r"veterinarian.{0,30}leadership|leadership.{0,30}veterinarian",
            r"job.?satisfaction.{0,30}(?:shelter|veterinarian)|(?:shelter|veterinarian).{0,30}job.?satisfaction",
            r"veterinarian.?of.?record",
            r"collaborative.?dynamic|exploring.{0,20}veterinarian.{0,20}leadership",
            r"key.{0,20}factor.{0,20}shelter.{0,20}veterinary|shelter.{0,20}veterinary.{0,20}job",
            r"unlocking.{0,20}collaborative",
            r"veterinarian.{0,20}relationships?.{0,20}(?:shelter|animal|administrator)",
            r"differences?.{0,20}expectations?.{0,20}(?:veterinarian|administrator)",
        ],
        "shelter-management/03_management_leadership.html",
        "Shelter Management",
    ),
    # --- Data Analysis ---
    (
        [
            r"big.?data|data.?science",
            r"model.?selection.{0,30}(?:dog|shelter|intake)|(?:dog|shelter|intake).{0,30}model.?selection",
            r"dog.?intake.{0,30}socioeconomic|socioeconomic.{0,30}intake",
        ],
        "shelter-management/05_data_analysis.html",
        "Shelter Management",
    ),
    # --- Mental Health / Staff Wellbeing ---
    (
        [
            r"compassion.?fatigue|secondary.?traumatic.?stress",
            r"well.?being.{0,20}(?:staff|shelter.?worker)|(?:staff|shelter.?worker).{0,20}well.?being",
            r"adverse.?childhood|ACE\b",
            r"professional.?quality.?of.?life",
            r"moral.?distress|burnout",
            r"tired.{0,20}(?:bones|stress)|shelter.{0,20}worker.{0,20}(?:fatigue|stress)",
        ],
        "shelter-management/06_mental_health.html",
        "Shelter Management",
    ),
    # --- Regulatory (shelter management level) ---
    (
        [
            r"breed.?specific.?legislation.{0,30}shelter|shelter.{0,30}breed.?specific",
            r"canine.{0,30}outcomes?.{0,30}breed.?specific|breed.?specific.{0,30}canine.{0,30}outcomes?",
        ],
        "shelter-management/07_regulatory.html",
        "Shelter Management",
    ),
    # --- Resource Allocation ---
    (
        [
            r"compensation.{0,30}survey|survey.{0,30}compensation|salary.{0,30}shelter|shelter.{0,30}salary",
            r"resource.?allocation",
        ],
        "shelter-management/09_resource_allocation.html",
        "Shelter Management",
    ),
    # =========================================================================
    # COMPANION ANIMAL HOMELESSNESS: Adoption & Placement
    # Placed BEFORE behavioral health so "post-adoption + socialization" papers
    # go to adoption rather than behavioral assessment
    # =========================================================================
    (
        [
            r"adopt(?:ion|er|ed|s)\b",
            r"kennel.{0,30}viewing|viewing.{0,30}kennel",
            r"off.site.{0,20}adoption|adoption.{0,20}off.site",
            r"rehome|re.home",
            r"return.to.owner",
            r"slow.track.{0,20}dog|dog.{0,20}slow.track",
            r"post.adoption|adopter.{0,20}satisfaction",
            r"inbetweener",
            r"shelter.{0,20}to.{0,20}home.{0,20}survey|shelter.to.home",
            r"optimis.{0,20}shelter.{0,20}outcomes",
            r"factors?.{0,20}affecting.{0,20}(?:likelihood|return).{0,20}(?:owner|reunif)",
            r"return.{0,20}to.{0,20}their.{0,20}owners?",
        ],
        "companion-animal-homelessness/adoption_placement_hub.html",
        "Companion Animal Homelessness",
    ),
    # =========================================================================
    # BEHAVIORAL HEALTH
    # =========================================================================
    # --- Assessment & Decision Making ---
    (
        [
            r"behavior.{0,20}assessment|behaviour.{0,20}assessment",
            r"socialization.{0,20}likelihood|likelihood.{0,20}socialization",
            r"SAFER\b",
            r"adoption.{0,20}potential.{0,20}undersociali|undersociali.{0,20}(?:cat|kitten).{0,20}adoption",
            r"increasing.{0,20}adoption.{0,20}potential.{0,20}undersociali",
        ],
        "behavioral-health/03_assessment_decision_making.html",
        "Behavioral Health",
    ),
    # --- Body Language ---
    (
        [
            r"body.?language",
            r"kitten.{0,20}fear.{0,20}video|video.{0,20}kitten.{0,20}fear",
            r"fear.{0,20}(?:behavior|behaviour).{0,20}identif|identif.{0,20}fear.{0,20}(?:behavior|behaviour)",
            r"fear.{0,20}rating|rating.{0,20}fear",
        ],
        "behavioral-health/04_body_language.html",
        "Behavioral Health",
    ),
    # --- Psychoactive Medications ---
    (
        [
            r"psychoactive|psychotropic",
            r"behavior.{0,20}med(?:ication)|behaviour.{0,20}med(?:ication)",
            r"pharmacol.{0,20}behav|behav.{0,20}pharmacol",
        ],
        "behavioral-health/09_behaviour_medications.html",
        "Behavioral Health",
    ),
    # =========================================================================
    # COMMUNITY & PUBLIC HEALTH
    # =========================================================================
    # --- Zoonotic Disease ---
    (
        [
            r"zoonotic.{0,30}(?:intestinal|parasit|disease)|zoonos",
            r"zoonotic.{0,20}(?:and.{0,20}non.{0,20}zoonotic|parasit)",
        ],
        "community-public-health/02_zoonotic_disease.html",
        "Community and Public Health",
    ),
    # --- Animal Cruelty ---
    (
        [r"cruelty|forensic.{0,20}animal|animal.{0,20}forensic"],
        "community-public-health/01_animal_cruelty.html",
        "Community and Public Health",
    ),
    # --- Dog Bites / Public Safety ---
    (
        [r"dog.?bite|bite.{0,20}attack|public.?safety.{0,20}dog"],
        "community-public-health/03_animals_public_safety.html",
        "Community and Public Health",
    ),
    # --- Rabies Epidemiology ---
    (
        [
            r"rabies.{0,40}epidemiology|epidemiology.{0,40}rabies",
            r"rabies.{0,30}control|control.{0,30}rabies",
        ],
        "community-public-health/04_rabies.html",
        "Community and Public Health",
    ),
    # --- Reportable/Emerging ---
    (
        [
            r"HPAI.{0,30}surveillance|surveillance.{0,30}HPAI",
            r"reportable.{0,20}disease|emerging.{0,20}disease",
        ],
        "community-public-health/05_reportable_emerging.html",
        "Community and Public Health",
    ),
    # =========================================================================
    # COMPANION ANIMAL HOMELESSNESS (other)
    # =========================================================================
    # --- Shelter Diversion ---
    (
        [
            r"diversion|surrender.{0,20}prevention",
            r"urgent.?care.{0,20}foster|foster.{0,20}urgent.?care",
            r"owner.?support",
        ],
        "companion-animal-homelessness/shelter_diversion_hub.html",
        "Companion Animal Homelessness",
    ),
    # --- Transport ---
    (
        [r"transport|relocation.{0,20}animal|animal.{0,20}relocation"],
        "companion-animal-homelessness/animal_transport_relocation_hub.html",
        "Companion Animal Homelessness",
    ),
    # =========================================================================
    # ANIMALS & PUBLIC POLICY: Legislation
    # (breed-specific POLICY framing — not shelter outcomes which go to 07_regulatory)
    # =========================================================================
    (
        [
            r"ordinance.{0,40}(?:playing|implementing|feline|lifesaving)|playing.{0,20}(?:cards|ordinance)",
            r"legislation.{0,30}(?:feline|cat|lifesaving)",
            r"policy.{0,30}breed|breed.{0,30}policy",
        ],
        "animals-public-policy/03_legislation.html",
        "Animals and Public Policy",
    ),
    # =========================================================================
    # RESEARCH & BIOSTATS
    # =========================================================================
    # --- Study Design ---
    (
        [
            r"scientific.?writing|study.?design|methodology",
            r"mixed.?method",
            r"(?:journey|from).{0,20}(?:idea|publication).{0,20}(?:shelter|publication|writing)",
        ],
        "research-biostats/study_design_hub.html",
        "Research and Biostats",
    ),
    # --- Epidemiology ---
    (
        [
            r"seroprevalence",
            r"epidemiology.{0,20}method|disease.?model",
        ],
        "research-biostats/epidemiology_biostats_hub.html",
        "Research and Biostats",
    ),
    # =========================================================================
    # PHYSICAL HEALTH: Facility & Shelter Design
    # (placed after adoption so "kennel" adoption papers don't land here)
    # =========================================================================
    (
        [
            r"cat.?den\b|den.{0,15}cat",
            r"inclusion.{0,20}cat.{0,20}den|cat.{0,20}den.{0,20}(?:shelter|population|upper.?respir)",
            r"cage.{0,30}design|housing.?design",
            r"facility.{0,30}design|shelter.?design",
            r"URI.{0,50}length.?of.?stay|length.?of.?stay.{0,50}URI",
            r"upper.{0,20}respiratory.{0,20}(?:infection|length.{0,5}stay)",
        ],
        "physical-health/facility_shelter_design_hub.html",
        "Physical Health of Animal",
    ),
    # =========================================================================
    # PHYSICAL HEALTH: Surgery & Anesthesia
    # Placed LAST among physical health — broad spay/neuter terms that don't
    # match more specific categories above
    # =========================================================================
    (
        [
            r"ovariohysterectomy|castration",
            r"anesth(?:esia|etic|etics)|anaesth(?:esia|etic)",
            r"analges(?:ia|ic|ics)",
            r"local.?(?:block|anaesth|anesth)",
            r"hypothermia.{0,30}(?:anesth|spay|neuter)|(?:anesth|spay|neuter).{0,30}hypothermia",
            r"perioperative.?warm|insulation.{0,30}(?:anesth|temperature|material)",
            r"peripheral.{0,20}warming",
            r"pedicle.?tie|ovarian.?pedicle.?tie",
            r"scrotal.?hematoma|scrotal.?haematoma",
            r"spermatic.?cord|autoligation",
            r"dermoid|enucleation",
            r"vulvar.?hemorrhage|vulvar.?haemorrhage",
            r"anesthetic.{0,20}(?:protocol|analgesic)|analgesic.{0,20}protocol.{0,20}spay",
            r"WSAVA.{0,30}(?:reproduction|guideline)|(?:reproduction|guideline).{0,30}WSAVA",
            r"spay.{0,20}neuter.{0,20}(?:clinic|survey|practice|protocol|technique)",
            r"surgical.{0,20}(?:steril|technique|castrat)",
            r"epinephrine.{0,20}scrot|scrot.{0,20}epinephrine",
            r"corneal.{0,20}dermoid|enucleation.{0,20}alternat",
            r"local.{0,20}anesthetic.{0,20}(?:blockade|block).{0,20}(?:castration|feline|cat)",
            r"HQHVSN.{0,20}setting",
        ],
        "physical-health/surgery_anesthesia_hub.html",
        "Physical Health of Animal",
    ),
    # =========================================================================
    # PHYSICAL HEALTH: Vaccination (broader terms — placed after TNR/community-cats)
    # =========================================================================
    (
        [
            r"vaccin(?:ation|e|ated)\b",
        ],
        "physical-health/vaccination_hub.html",
        "Physical Health of Animal",
    ),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def run_pdftotext(pdf_path: Path) -> str:
    """Run pdftotext -layout and return stdout text (or empty string on error)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def derive_title(filename: str) -> str:
    """
    Derive a clean article title from the PDF filename.

    Strips:
    - .pdf extension
    - trailing ' [Abstract]' (case-insensitive)
    - trailing '_ Journal of Shelter Medicine and Community Animal Health'
      and variants (with/without underscores)
    - trailing whitespace / underscores
    """
    name = filename
    if name.lower().endswith(".pdf"):
        name = name[:-4]

    # Strip JSMCAH suffix (various forms)
    jsmcah_pattern = re.compile(
        r"\s*[_|]\s*Journal of Shelter Medicine and Community Animal Health.*$",
        re.IGNORECASE,
    )
    name = jsmcah_pattern.sub("", name)

    # Strip trailing [Abstract]
    name = re.sub(r"\s*\[Abstract\]\s*$", "", name, flags=re.IGNORECASE)

    # Strip trailing _ or | separators
    name = name.strip("_| \t")

    # Normalise internal whitespace
    name = re.sub(r"\s+", " ", name).strip()

    return name


def make_slug(title: str) -> str:
    """Convert title to a lowercase hyphenated slug, max 80 chars."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if len(slug) > 80:
        slug = slug[:80].rstrip("-")
    return slug


def dedupe_slug(slug: str, existing: set) -> str:
    """If slug already in existing, append -2, -3, etc."""
    if slug not in existing:
        return slug
    i = 2
    while f"{slug}-{i}" in existing:
        i += 1
    return f"{slug}-{i}"


# ---------------------------------------------------------------------------
# Abstract extraction
# ---------------------------------------------------------------------------

def extract_abstract(text: str):
    """
    Extract abstract from PDF text.

    Returns (abstract_text, status) where status is one of:
      'yes'        – found via standard heading
      'uncertain'  – fallback to first substantial block
      'NO'         – nothing usable found
    """
    if not text:
        return ("", "NO")

    # Strategy 1: Standard "Abstract" or "Summary" heading
    # Look for a line containing only "Abstract" or "Summary" (case-insensitive)
    # and grab text until next heading.

    end_markers = [
        # Require section-heading form: keyword at start of line followed by
        # optional whitespace then EITHER a colon OR end-of-line (i.e. the word
        # alone on the line).  Using \b only would fire on body-text phrases like
        # "methods for tracking…" or "introduction of…", truncating abstracts.
        r"^\s*(?:1\.?\s*)?Introduction\s*(?::|$)",
        r"^\s*Keywords?\s*:",
        r"^\s*Background\s*(?::|$)",
        r"^\s*(?:1\.?\s*)?Methods?\s*(?::|$)",
        r"^\s*Results?\s*(?::|$)",
        r"^\s*Discussion\s*(?::|$)",
        r"^\s*Conclusions?\s*(?::|$)",
        r"^\s*References?\s*(?::|$)",
        r"^\s*Table\s+\d+",
    ]
    end_re = re.compile("|".join(end_markers), re.IGNORECASE | re.MULTILINE)

    # Match "Abstract" as a standalone heading (possibly after article type line)
    # In JSMCAH format, "Abstract" appears right before the abstract text on the
    # same section.  Some two-column PDFs have metadata (Received:…) appended
    # after many spaces on the same line as the heading — allow trailing non-word
    # content before the newline.
    abstract_heading_re = re.compile(
        r"(?:^|\n)\s*(?:Abstract|Summary)[ \t]*(?:[^\S\n]{5,}\S[^\n]*)?\n",
        re.IGNORECASE,
    )

    m = abstract_heading_re.search(text)
    if m:
        start = m.end()
        end_m = end_re.search(text, start)
        end = end_m.start() if end_m else start + 5000
        raw = text[start:end].strip()
        raw = clean_abstract(raw)
        if len(raw) > 80:
            return (raw, "yes")

    # Strategy 2: JSMCAH [Abstract] web-exported PDFs
    # These have "ABSTRACT" in caps followed by the body text
    abs_caps_re = re.compile(
        r"(?:^|\n)\s*ABSTRACT\s*\n",
        re.IGNORECASE,
    )
    m = abs_caps_re.search(text)
    if m:
        start = m.end()
        # Find ending — could be "Keywords" or a long gap or end of doc section.
        # NOTE: do NOT include a "N of M" page-number pattern here because
        # the $ metachar with MULTILINE would inadvertently match mid-abstract.
        end_m = re.search(
            r"\n\s*(?:Keywords?|Citation:)\s",
            text[start:],
            re.IGNORECASE | re.MULTILINE,
        )
        end = (start + end_m.start()) if end_m else start + 5000
        raw = text[start:end].strip()
        raw = clean_abstract(raw)
        if len(raw) > 80:
            return (raw, "yes")

    # Strategy 3: For full-article PDFs that have structured abstract with
    # labelled sections: "Introduction:", "Methods:", "Results:", "Conclusion:"
    structured_re = re.compile(
        r"(?:Introduction|Background)\s*:(.+?)(?:\n\s*(?:Key|Reference|\d+\s+Journal))",
        re.IGNORECASE | re.DOTALL,
    )
    # Actually let's try to grab the full structured abstract section
    # by looking for Introduction: ... Conclusion: ... block
    struct_full_re = re.compile(
        r"(?:Introduction|Background)\s*:.+?(?:Conclusion[s]?\s*:.+?\.\s*\n)",
        re.IGNORECASE | re.DOTALL,
    )
    m = struct_full_re.search(text[:3000])
    if m:
        raw = clean_abstract(m.group(0))
        if len(raw) > 80:
            return (raw, "yes")

    # Strategy 4: Fallback — grab first substantial paragraph block
    # (skip header lines, find a block of text > 200 chars)
    lines = text.split("\n")
    blocks = []
    current_block = []
    for line in lines[:100]:  # Only scan first 100 lines
        stripped = line.strip()
        if stripped:
            current_block.append(stripped)
        else:
            if current_block:
                block_text = " ".join(current_block)
                if len(block_text) > 150:
                    blocks.append(block_text)
                current_block = []
    if current_block:
        block_text = " ".join(current_block)
        if len(block_text) > 150:
            blocks.append(block_text)

    if blocks:
        # Skip very short first blocks (likely titles/author lines)
        candidate = None
        for b in blocks:
            # Skip if it looks like just a title/author block
            if len(b) > 200:
                candidate = b
                break
        if not candidate and blocks:
            candidate = blocks[-1] if len(blocks) > 1 else blocks[0]
        if candidate and len(candidate) > 80:
            return (clean_abstract(candidate[:3000]), "uncertain")

    return ("", "NO")


def clean_abstract(text: str) -> str:
    """Clean up extracted abstract text: fix whitespace, remove page artefacts."""
    # --- Fix 1: de-hyphenate line-wrapped words (BEFORE whitespace collapse) ---
    # pdftotext -layout often splits a word across a line break with a hyphen,
    # e.g. "culmi-\n   nating" → should be "culminating".
    # Rule: lowercase-letter + hyphen at end of line, followed by lowercase on next line.
    text = re.sub(r'([a-zA-Z])-\s*\n\s*([a-z])', r'\1\2', text)

    # --- Fix 2: strip date/correspondence metadata noise (BEFORE joining lines) ---
    # JSMCAH two-column PDFs use -layout which places each row's right-column
    # content at the end of the same text line, separated by many spaces.
    # Metadata labels (Received/Revised/Accepted/Published/Correspondence/
    # Funding/Editor/Reviewers) appear in the right column alongside abstract
    # prose in the left column.  Strategy:
    #
    # (a) For lines with BOTH left-column prose AND right-column metadata:
    #     strip from the first occurrence of ≥10 spaces followed by a metadata
    #     keyword onwards (right-column fragment at end of line).
    #
    # (b) For lines that are ENTIRELY a right-column fragment (i.e. the first
    #     non-space character is at column ≥70, meaning no left-column content):
    #     skip the line entirely if it matches a metadata/address pattern.
    #
    # We use the column position heuristic: if len(line) - len(line.lstrip()) ≥ 70
    # then there is no left-column content on this line.

    # For lines with LEFT-column prose AND right-column content:
    # Strip everything after ≥40 consecutive spaces (that's where the right column starts).
    # This handles metadata labels, reviewer names, addresses, email fragments, etc.
    right_col_any_re = re.compile(r"\s{40,}.*$")

    # Metadata/address keywords for right-col-only lines (leading_spaces ≥ 70)
    _meta_kw = re.compile(
        r"(?:Received|Revised|Accepted|Published|Correspondence|Funding|"
        r"Email|Editor|Reviewers?|Citation|PO Box|P\.O\. Box)\s*[:,]?",
        re.IGNORECASE,
    )

    lines = text.split("\n")
    cleaned = []
    for line in lines:
        # Strip form-feed characters (PDF page breaks in pdftotext output)
        line = line.replace("\x0c", "")
        stripped = line.strip()
        if not stripped:
            continue
        # Skip URL-only lines, page header lines (title + URL), page number lines,
        # and journal citation footers.
        if re.match(r"^https?://\S+", stripped):
            continue
        # Lines that contain a URL — these are page headers from pdftotext layout
        # (after form-feed removal the title+URL line reads as "Title... https://url")
        if re.search(r"\s+https?://\S+", stripped):
            continue
        # Page number lines: "N of M" optionally followed by date/time stamps
        if re.match(r"^\d+\s+of\s+\d+\b", stripped):
            continue
        if re.match(r"^Journal of Shelter Medicine", stripped, re.IGNORECASE):
            continue
        if re.match(r"^Citation:\s+Journal", stripped, re.IGNORECASE):
            continue
        # Skip lines that consist ONLY of a metadata label + date/name.
        # These appear when the raw abstract text starts with a right-column
        # metadata line that has been stripped of its leading whitespace.
        # Examples: "Received: 31 October 2025", "Correspondence", "*Emily Hunt"
        if re.match(
            r"^(?:Received|Revised|Accepted|Published|Correspondence|Funding|"
            r"Editor|Reviewers?)\s*:?\s*\S[^\n]{0,80}$",
            stripped,
            re.IGNORECASE,
        ):
            continue
        # Detect lines whose first non-space char is at column ≥70 (right-col only).
        # These are lines where there is NO left-column content, only right-column
        # metadata/address/reviewer text.  Skip them entirely.
        leading_spaces = len(line) - len(line.lstrip(" "))
        if leading_spaces >= 70:
            # Skip: metadata keyword, names/addresses (starting uppercase), email
            # fragments (containing @, or ending in .edu/.com/.org etc.), or any
            # short fragment that is clearly not abstract prose.
            if (
                _meta_kw.search(stripped)
                or re.match(r"^\*?[A-Z]", stripped)
                or re.search(r"@|\.edu\b|\.com\b|\.org\b|\.net\b", stripped, re.IGNORECASE)
                or len(stripped) < 60  # very short right-col-only fragments are noise
            ):
                continue
        # Strip right-column content from end of lines that have left-column prose.
        # Any content after ≥40 consecutive spaces is right-column artefact.
        line = right_col_any_re.sub("", line)
        stripped = line.strip()
        if stripped:
            cleaned.append(stripped)

    text = " ".join(cleaned)

    # After joining, also strip any remaining inline date-metadata fragments.
    # Only match the specific pattern: label + colon + date string (e.g. "31 October 2025")
    # or "label: short-word-run" that looks like a date/name, NOT followed by regular prose.
    # We match: label, colon, optional spaces, then up to ~60 non-semicolon chars that end at
    # a digit-year (for date lines) or at the next metadata label.
    inline_date_re = re.compile(
        r"(?:Received|Revised|Accepted|Published)\s*:\s*\d[^;]{0,60}?(?=\s+[A-Z]|\s*(?:Received|Revised|Accepted|Published|Correspondence)|$)",
        re.IGNORECASE,
    )
    text = inline_date_re.sub("", text)

    # Remove standalone email addresses (word@word.tld patterns)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w{2,}\b", "", text)

    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    # --- Fix 1b: de-hyphenate collapsed form "culmi- nating" (after whitespace collapse) ---
    # After joining lines, some artifacts become "word- word" (hyphen + space between
    # lowercase fragments). Only join when BOTH sides are lowercase — this preserves
    # legitimate hyphenated compounds like "spay-neuter" (no space after hyphen) and
    # "high-Volume" (uppercase continuation). Pattern: lowercase char, hyphen, one-or-more
    # spaces, lowercase char.
    text = re.sub(r'([a-z])-\s+([a-z])', r'\1\2', text)

    # Fix common run-together words from PDF layout
    text = text.strip()
    return text


# ---------------------------------------------------------------------------
# Fix 3: byline-only detection
# ---------------------------------------------------------------------------

# Article-type header words that often appear at the top of no-abstract pages.
_ARTICLE_TYPE_RE = re.compile(
    r"^\s*(?:OPINION|SPECIAL|COMMUNITY|REVIEW|RESEARCH|ORIGINAL|BRIEF|COMMENTARY|"
    r"EDITORIAL|LETTER|PERSPECTIVE)\s*(?:ARTICLE|REPORT|COMMUNICATION)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Lines that look like author names or affiliations (not prose).
# Use word boundaries for institution keywords to avoid false matches on words
# like "sheltered", "animal welfare" (which are genuine prose), "society" etc.
_AFFILIATION_LINE_RE = re.compile(
    r"^(?:[A-Z][a-z]+ )+[A-Z][a-z]+\d*(?:\s*[,;]\s*(?:[A-Z][a-z]+ )*[A-Z][a-z]+\d*)*\s*$|"
    r"\b(?:University|College|Institute|School of |Department of |Faculty of |Hospital|"
    r"Laboratory|Humane Society|Inc\.|Ltd\.)\b",
    re.IGNORECASE,
)

# A keywords line.
_KEYWORDS_LINE_RE = re.compile(r"^\s*keywords?\s*:", re.IGNORECASE)


def is_byline_only(abstract: str) -> tuple:
    """
    Return (True, reason) when the extracted text contains no real abstract prose.

    Heuristic: after removing article-type headers, keywords lines, and
    author-name/affiliation lines, if < ~250 chars of prose remain the record
    is considered byline-only and should be excluded.

    Also returns True when the text is dominated by a Keywords block with no
    preceding prose (< 80 chars before "Keywords:").

    Returns (False, "") when real content is present.
    """
    text = abstract.strip()
    if not text:
        return (True, "empty text")

    # Check: dominated by a Keywords line at the start
    kw_match = _KEYWORDS_LINE_RE.search(text)
    if kw_match and kw_match.start() < 120:
        before_kw = text[: kw_match.start()].strip()
        # If almost nothing precedes the Keywords line it's not a real abstract
        if len(before_kw) < 80:
            return (True, "only keywords list (no prose before Keywords:)")

    # Strip article-type header lines
    remaining = _ARTICLE_TYPE_RE.sub("", text)

    # Strip keyword lines
    lines_after = []
    for line in remaining.split("\n"):
        if _KEYWORDS_LINE_RE.match(line):
            continue
        lines_after.append(line)
    remaining = "\n".join(lines_after)

    # Strip affiliation-like lines
    prose_lines = []
    for line in remaining.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if _AFFILIATION_LINE_RE.search(stripped) and len(stripped) < 200:
            continue
        prose_lines.append(stripped)

    prose = " ".join(prose_lines).strip()

    # Remove any residual article-type words at the very start
    prose = re.sub(
        r"^(?:OPINION|SPECIAL|COMMUNITY|REVIEW|ORIGINAL|BRIEF|COMMENTARY|"
        r"EDITORIAL|LETTER|PERSPECTIVE)\s+(?:ARTICLE|REPORT|COMMUNICATION)?\s*",
        "",
        prose,
        flags=re.IGNORECASE,
    ).strip()

    if len(prose) < 250:
        return (True, f"only byline/affiliations — {len(prose)} chars prose after stripping")

    return (False, "")


# Known IDs that are definitely byline-only (belt-and-suspenders guard).
# These are prefix-matched against the generated slug (which may be longer due to
# the 80-char truncation in make_slug).
_KNOWN_BYLINE_ONLY_PREFIXES = [
    "an-inconvenient-truth",          # "An Inconvenient Truth targeted TNR..."
    "an-asv-critique",                 # "An ASV Critique The 2024 WSAVA..."
    "ethics-committees-for-animal",    # "Ethics Committees for Animal Shelters"
    "telemedicine-access-to-veterinary",  # "Telemedicine, Access to Vet Healthcare..."
    "cat-friendly-principles-for",     # "Cat friendly principles for those working..."
    "managing-cat-populations",        # "Managing cat populations based on..."
    "outcomes-for-kittens-born",       # "Outcomes for kittens born to free-roaming..."
    "identifying-solutions-for",       # "identifying solutions for 'inbetweener' cats"
    "comparison-of-the-number-of-dog", # "Comparison of the Number of Dog Adoptions..."
]


def _is_known_byline_only(slug: str) -> bool:
    """Return True if slug starts with any known byline-only prefix."""
    return any(slug.startswith(p) for p in _KNOWN_BYLINE_ONLY_PREFIXES)

NEEDS_WEB_ABSTRACT_PATH = str(TOOLS_DIR / "needs_web_abstract.md")


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_year(text: str, filename: str):
    """
    Extract publication year from text or filename.
    Valid range: 2021–2026.
    """
    # Look for 'Published:' or 'Accepted:' date lines
    for pat in [
        r"Published\s*:\s*.*?(202[1-6])",
        r"Accepted\s*:\s*.*?(202[1-6])",
        r"Revised\s*:\s*.*?(202[1-6])",
        r"Received\s*:\s*.*?(202[1-6])",
        r"\((202[1-6])\)",
        r"\b(202[1-6])\b",
    ]:
        m = re.search(pat, text[:5000])
        if m:
            year = int(m.group(1))
            if 2021 <= year <= 2026:
                return year

    # Fallback: scan filename
    m = re.search(r"\b(202[1-6])\b", filename)
    if m:
        return int(m.group(1))

    # Second pass: any year mention in text
    m = re.search(r"\b(202[1-6])\b", text[:10000])
    if m:
        return int(m.group(1))

    return None


def _clean_authors_string(authors: str) -> str:
    """
    Clean an author string extracted from PDF text for display.

    Steps:
    1. Cut at the first ";" — everything from the first semicolon onward is
       affiliation / address noise.
    2. Strip trailing superscript digits and asterisks from each name token
       (e.g. "Guilfoyle1*" → "Guilfoyle", "Sokol2" → "Sokol").
    3. Collapse whitespace and trim.
    4. If the result is empty or clearly junk, return "".
    """
    if not authors:
        return ""

    # Step 1: cut at first semicolon
    if ";" in authors:
        authors = authors[: authors.index(";")]

    # Step 2: strip trailing digit-runs and asterisks from each token
    # Match a word boundary followed by a name token ending in digits/asterisks.
    # We target tokens that end in [0-9*]+ where the preceding char is a letter.
    authors = re.sub(r'([A-Za-z])(\d+\*?|\*)', r'\1', authors)

    # Step 3: collapse whitespace and trim
    authors = re.sub(r'\s+', ' ', authors).strip()
    # Strip any trailing commas or "and" fragments left after cut
    authors = authors.rstrip(",").strip()
    if authors.lower().endswith(" and"):
        authors = authors[:-4].strip()

    # Step 4: sanity check — if the remaining string still looks like an address
    # (digits at start, or contains institution keywords that crept in before the ";")
    if re.match(r'^\d', authors):
        return ""
    _AFF_KW = re.compile(
        r'\b(?:University|Society|Diagnostics|Hospital|Institute|College|'
        r'Department|LLC|Inc|Ltd|Laboratory|Humane)\b',
        re.IGNORECASE,
    )
    if _AFF_KW.search(authors):
        # Cut at the first affiliation keyword token
        m = _AFF_KW.search(authors)
        authors = authors[: m.start()].strip().rstrip(",").strip()

    return authors


def extract_authors(text: str) -> str:
    """
    Try to extract author names from PDF text (first page).
    Returns a cleaned string or "" if not found.
    """
    # Authors typically appear after the title (first 1-2 lines) and before abstract
    # They often follow the pattern: Firstname Lastname1 and Firstname Lastname2
    # Or "Lastname F, Lastname2 G"
    lines = text.split("\n")
    # Skip first line (usually article type), then title, then look for author-like lines
    candidate_lines = []
    for i, line in enumerate(lines[:20]):
        stripped = line.strip()
        if not stripped:
            continue
        # Skip article type lines
        if re.match(r"^\s*(ORIGINAL RESEARCH|OPINION|CASE REPORT|REVIEW|COMMENTARY|BRIEF|COMMUNITY)", stripped, re.IGNORECASE):
            continue
        # Author lines often have initials, multiple names, affiliations markers
        # or explicit "and" between names
        if re.search(r"\b(and|,)\s+[A-Z][a-z]", stripped) or re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+\s*\d*\s+and\b", stripped):
            if len(stripped) < 300:  # author lines are not too long
                candidate_lines.append(stripped)

    if candidate_lines:
        raw = "; ".join(candidate_lines[:2])
        return _clean_authors_string(raw)

    # Try simpler: look for lines with multiple capitalized names
    for line in lines[1:15]:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip if it looks like an address or institution (contains University, USA, etc.)
        if re.search(r"University|College|Institute|Society|Department|Hospital|Clinic|Inc\.|Ltd\.", stripped, re.IGNORECASE):
            continue
        # Skip long text
        if len(stripped) > 200:
            continue
        # Author-like: starts with capital letter, contains name patterns
        names = re.findall(r"[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+", stripped)
        if len(names) >= 1:
            return _clean_authors_string(stripped)

    return ""


def extract_journal(text: str) -> str:
    """Extract journal name from text."""
    # JSMCAH citation line
    m = re.search(
        r"Journal of Shelter Medicine and Community Animal Health",
        text[:5000],
        re.IGNORECASE,
    )
    if m:
        return "Journal of Shelter Medicine and Community Animal Health"

    # Citation line pattern
    m = re.search(r"Citation:\s+(.+?)\s+20\d{2}", text[:5000])
    if m:
        j = m.group(1).strip()
        if len(j) < 150:
            return j

    return ""


def extract_doi(text: str) -> str:
    """Extract DOI from text."""
    # Pattern: doi: or DOI: or http://dx.doi.org/ or https://doi.org/
    for pat in [
        r"(?:doi|DOI)[:\s]+([^\s,\n]+)",
        r"https?://(?:dx\.)?doi\.org/([^\s\n]+)",
        r"http://dx\.doi\.org/([^\s\n]+)",
    ]:
        m = re.search(pat, text[:5000])
        if m:
            doi = m.group(1).strip().rstrip(".")
            # Validate: DOI should start with 10.
            if doi.startswith("10."):
                return doi
            # If the full URL pattern was matched, group(1) is the path
    return ""


def extract_year_from_citation(text: str):
    """Extract year from 'Journal of Shelter Medicine ... 20XX' citation lines."""
    m = re.search(
        r"Journal of Shelter Medicine.*?(\d{4})",
        text[:5000],
    )
    if m:
        year = int(m.group(1))
        if 2021 <= year <= 2026:
            return year
    return None


def build_citation(title: str, authors: str, journal: str, year, doi: str) -> str:
    """Build a formatted citation string from available parts."""
    parts = []
    if authors:
        parts.append(authors)
    if title:
        parts.append(title + ".")
    if journal:
        parts.append(journal + ".")
    if year:
        parts.append(str(year) + ".")
    if doi:
        parts.append(f"doi:{doi}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Subdomain mapping
# ---------------------------------------------------------------------------

def guess_subdomain(title: str, text: str):
    """
    Map article to the best-fit subdomain page.

    Strategy: Apply title-only matching first with ALL rules (to avoid
    false positives from body text). Then fall back to title+text matching.

    Returns (subdomain_page, domain_name, note)
    """
    title_only = title.lower()
    full_text = (title + " " + text[:3000]).lower()

    # Pass 1: Title-only matching — catches clear cases without body-text noise
    for patterns, page, domain in DOMAIN_RULES:
        for pat in patterns:
            if re.search(pat, title_only, re.IGNORECASE):
                return (page, domain, "")

    # Pass 2: Title + abstract text matching — needed for articles with less
    # descriptive titles or where the title alone doesn't match a rule
    for patterns, page, domain in DOMAIN_RULES:
        for pat in patterns:
            if re.search(pat, full_text, re.IGNORECASE):
                return (page, domain, "")

    return (
        "physical-health/medical_health_hub.html",
        "Physical Health of Animal",
        "UNMAPPED — defaulted; review needed",
    )


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_pdfs() -> None:
    pdf_files = sorted(SOURCE_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files in source directory.")

    records = []
    report_rows = []
    needs_web: list = []  # byline-only records for needs_web_abstract.md
    used_slugs: set[str] = set()

    for pdf_path in pdf_files:
        filename = pdf_path.name
        title = derive_title(filename)
        print(f"  Processing: {filename[:60]}...")

        # Extract text
        text = run_pdftotext(pdf_path)

        # Extract abstract
        abstract, abs_status = extract_abstract(text)

        # If no abstract extractable, exclude from catalog but log in report
        if not abstract or abs_status == "NO":
            report_rows.append({
                "filename": filename,
                "year": "N/A",
                "subdomain_page": "EXCLUDED",
                "abs_status": "NO",
                "note": "No extractable abstract; excluded from catalog",
            })
            print(f"    -> EXCLUDED (no abstract)")
            continue

        # Fix 3: Check for byline-only / no-real-abstract records.
        # Derive a slug now (before we know if we'll keep the record) for the
        # known-slugs guard.  We'll re-derive it properly below if we keep it.
        _candidate_slug = make_slug(title)
        byline_only, byline_reason = is_byline_only(abstract)
        if byline_only or _is_known_byline_only(_candidate_slug):
            reason = byline_reason or "matched known byline-only ID list"
            needs_web.append({
                "filename": filename,
                "title": title,
                "reason": reason,
            })
            report_rows.append({
                "filename": filename,
                "year": "N/A",
                "subdomain_page": "EXCLUDED",
                "abs_status": abs_status,
                "note": f"Byline-only — needs web abstract: {reason}",
            })
            print(f"    -> EXCLUDED (byline-only: {reason[:60]})")
            continue

        # Extract metadata
        year = extract_year(text, filename) or extract_year_from_citation(text)
        authors = extract_authors(text)
        journal = extract_journal(text)
        doi = extract_doi(text)

        # Validate year
        if year is None or not (2021 <= year <= 2026):
            # Try harder — scan whole text
            m = re.search(r"\b(202[1-6])\b", text)
            if m:
                year = int(m.group(1))
            else:
                report_rows.append({
                    "filename": filename,
                    "year": "N/A",
                    "subdomain_page": "EXCLUDED",
                    "abs_status": abs_status,
                    "note": "Year not in 2021-2026 range; excluded from catalog",
                })
                print(f"    -> EXCLUDED (year out of range)")
                continue

        # Subdomain mapping
        subdomain_page, domain, note = guess_subdomain(title, text)

        # If the subdomain_page file doesn't exist, skip
        full_page_path = REPO_ROOT / subdomain_page
        if not full_page_path.exists():
            note = f"Mapped page {subdomain_page} does not exist; EXCLUDED"
            report_rows.append({
                "filename": filename,
                "year": str(year),
                "subdomain_page": subdomain_page,
                "abs_status": abs_status,
                "note": note,
            })
            print(f"    -> EXCLUDED (page not found: {subdomain_page})")
            continue

        # Build slug and ensure uniqueness
        slug = make_slug(title)
        slug = dedupe_slug(slug, used_slugs)
        used_slugs.add(slug)

        # Build citation
        citation = build_citation(title, authors, journal, year, doi)
        if not citation:
            citation = title

        # Build record
        record = {
            "id": slug,
            "title": title,
            "authors": authors,
            "journal": journal or "Journal of Shelter Medicine and Community Animal Health",
            "year": year,
            "citation": citation,
            "doi": doi,
            "source": "folder",
            "abstract": abstract,
            "abstract_origin": f"pdf:{filename}",
            "domain": domain,
            "subdomain_page": subdomain_page,
            "mcqs": [],
        }

        # Validate
        problems = lib_catalog.validate_record(record)
        if problems:
            note_str = f"VALIDATION ERRORS: {'; '.join(problems)}"
            report_rows.append({
                "filename": filename,
                "year": str(year),
                "subdomain_page": subdomain_page,
                "abs_status": abs_status,
                "note": note_str,
            })
            print(f"    -> EXCLUDED (validation: {problems})")
            continue

        records.append(record)
        report_rows.append({
            "filename": filename,
            "year": str(year),
            "subdomain_page": subdomain_page,
            "abs_status": abs_status,
            "note": note if note else "ok",
        })
        print(f"    -> OK (year={year}, page={subdomain_page}, abstract={abs_status})")

    # --- Problem 3: carry over existing MCQs so re-extraction is non-destructive ---
    # Load the current catalog (if present) and build a map of id → mcqs.
    existing_mcqs: dict = {}
    if Path(CATALOG_PATH).exists():
        try:
            existing = lib_catalog.load_catalog(CATALOG_PATH)
            for existing_rec in existing:
                eid = existing_rec.get("id", "")
                mcqs = existing_rec.get("mcqs", [])
                if eid and mcqs:
                    existing_mcqs[eid] = mcqs
        except Exception:
            pass  # corrupted catalog — start fresh, no MCQs to carry over

    mcqs_restored = 0
    for rec in records:
        if rec["id"] in existing_mcqs:
            rec["mcqs"] = existing_mcqs[rec["id"]]
            mcqs_restored += 1

    if mcqs_restored:
        print(f"  (restored MCQs for {mcqs_restored} record(s) from existing catalog)")

    # Save catalog
    lib_catalog.save_catalog(CATALOG_PATH, records)
    print(f"\nSaved {len(records)} records to {CATALOG_PATH}")

    # Write report
    write_report(report_rows, records, needs_web)
    print(f"Report written to {REPORT_PATH}")

    # Write needs_web_abstract.md
    if needs_web:
        _write_needs_web(needs_web)
        print(f"needs_web_abstract.md: {len(needs_web)} entries → {NEEDS_WEB_ABSTRACT_PATH}")


def write_report(rows: list, records: list, needs_web: list) -> None:
    """Write extract_report.md."""
    lines = []
    lines.append("# Extract Report — ABVP Journal Folder PDFs\n")
    lines.append(f"Total PDFs processed: {len(rows)}\n")
    total_uncertain = sum(1 for r in rows if r["abs_status"] == "uncertain" and r["subdomain_page"] not in ("EXCLUDED",))
    total_excluded = sum(1 for r in rows if r["subdomain_page"] == "EXCLUDED" or r.get("note", "").startswith("VALIDATION"))
    lines.append(f"Records written to catalog: **{len(records)}**\n")
    lines.append(f"Abstract uncertain (included): {total_uncertain}\n")
    lines.append(f"Excluded (no abstract / byline-only / bad year / validation error): {total_excluded}\n")
    lines.append(f"Byline-only (needs web abstract): {len(needs_web)}\n\n")

    lines.append("## Per-file results\n")
    lines.append("| Filename | Year | Subdomain Page | Abstract | Note |\n")
    lines.append("|----------|------|----------------|----------|------|\n")
    for r in rows:
        fn = r["filename"].replace("|", "\\|")
        note_cell = r.get("note", "").replace("|", "\\|")
        lines.append(
            f"| {fn} | {r['year']} | {r['subdomain_page']} | {r['abs_status']} | {note_cell} |\n"
        )

    lines.append("\n## Mapping distribution by subdomain\n\n")
    from collections import Counter
    page_counts = Counter()
    for rec in records:
        page_counts[rec["subdomain_page"]] += 1
    for page, count in sorted(page_counts.items()):
        lines.append(f"- `{page}`: {count}\n")

    lines.append("\n## Excluded files\n\n")
    for r in rows:
        if r["subdomain_page"] == "EXCLUDED" or r.get("note", "").startswith("VALIDATION"):
            lines.append(f"- **{r['filename']}**: {r.get('note', 'excluded')}\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.writelines(lines)


def _write_needs_web(needs_web: list) -> None:
    """Write tools/needs_web_abstract.md listing byline-only records."""
    lines = []
    lines.append("# Needs Web Abstract\n\n")
    lines.append(
        "These records were excluded from `journal-catalog.json` because the PDF "
        "contains only a byline / article-type header / keywords list — no real abstract "
        "prose.  Fetch the abstract from the journal website and add the record manually.\n\n"
    )
    lines.append("| Filename | Derived Title | Reason |\n")
    lines.append("|----------|--------------|--------|\n")
    for item in needs_web:
        fn = item["filename"].replace("|", "\\|")
        title = item["title"].replace("|", "\\|")
        reason = item["reason"].replace("|", "\\|")
        lines.append(f"| {fn} | {title} | {reason} |\n")
    with open(NEEDS_WEB_ABSTRACT_PATH, "w", encoding="utf-8") as fh:
        fh.writelines(lines)


if __name__ == "__main__":
    process_pdfs()
