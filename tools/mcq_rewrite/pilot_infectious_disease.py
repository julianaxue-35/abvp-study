"""Pilot rewrite: Physical Health > Infectious Disease (hub-authored MCQs only).

Style target: ABVP Sample Examination Items (3 options a-c, one correct answer
and two plausible distractors, vignette / "which statement is correct" /
"X differs from Y in that" stems).

Each item: (topic, replaces[old dump indexes], stem, correct, wrong1, wrong2, explanation)
Answer letters are assigned by a seeded, position-balanced shuffle so the key is
not predictable. Nothing here touches mock-data.js or any hub page.

Run:  python3 pilot_infectious_disease.py   ->  writes pilot_infectious_disease.json
"""
import json, random, re, pathlib

HERE = pathlib.Path(__file__).parent

ITEMS = [
# ---------------- Canine parvovirus (CPV) ----------------
("Canine parvovirus", [6, 7],
 "A 4-month-old unvaccinated puppy has had 2 days of haemorrhagic diarrhoea and vomiting. A faecal antigen ELISA (SNAP) test is negative. The most appropriate next step is to",
 "isolate the puppy and submit faeces for quantitative PCR (qPCR).",
 "release the puppy from isolation because a negative result excludes canine parvovirus (CPV).",
 "manage as dietary indiscretion in the general ward and reassess in 48 hours.",
 "Faecal antigen tests are highly specific but insensitive (false negatives reach about 51%), so a negative result does not exclude CPV in a compatible case. Isolate and confirm with qPCR. Releasing the puppy or moving it to the general ward exposes susceptible animals."),

("Canine parvovirus", [9, 293],
 "A healthy adult dog is given a modified live virus (MLV) DAPP vaccine at intake. Ten days later it is bright and eating, with normal faeces, but a faecal parvovirus qPCR is positive. The most likely explanation is",
 "shedding of vaccine-derived virus.",
 "subclinical canine parvovirus (CPV) infection acquired from the shelter environment.",
 "cross-reactivity of the assay with canine coronavirus.",
 "Up to about 23% of recently MLV-vaccinated dogs are qPCR-positive between days 3 and 28. In a clinically normal dog this is interpreted cautiously and does not by itself indicate field infection. Because qPCR targets parvovirus nucleic acid, cross-reaction with coronavirus is not the usual explanation."),

("Canine parvovirus", [10, 11, 44],
 "Which finding within the first 24 hours of hospitalisation is the most reliable positive predictor of survival in a puppy with canine parvovirus (CPV) enteritis?",
 "A measurable rise in the absolute lymphocyte count",
 "Resolution of vomiting after the first antiemetic dose",
 "Normalisation of the packed cell volume by 24 hours",
 "An early lymphocyte rebound carries a 100% positive predictive value for survival. Vomiting can settle transiently and does not predict outcome, and the packed cell volume is driven by fluid status and gut blood loss rather than by recovery of the marrow."),

("Canine parvovirus", [12, 13],
 "After fluid resuscitation, a puppy with canine parvovirus (CPV) enteritis has fever, hypoglycaemia and signs of sepsis. Which antimicrobial combination is best supported for this puppy?",
 "Ampicillin plus amikacin",
 "Cefovecin plus metronidazole",
 "Enrofloxacin plus metronidazole",
 "Up to 72% of Gram-negative isolates from CPV sepsis resist third- and fourth-generation cephalosporins and metronidazole, so an ampicillin-plus-aminoglycoside backbone is preferred once the puppy is rehydrated (limiting nephrotoxicity). Fluoroquinolones are generally avoided in growing puppies."),

("Canine parvovirus", [19, 20, 40],
 "A 12-week-old puppy with parvoviral enteritis is 8% dehydrated, has a body condition score (BCS) of 5/9 and is bright and responsive. The shelter has no space in its isolation ward. Which plan is best supported?",
 "IV fluids for 24 hours, then step down to subcutaneous fluids and oral care in foster",
 "Subcutaneous fluids and oral care from admission, with IV fluids only if vomiting worsens",
 "Humane euthanasia, because treatment cannot be delivered safely without an isolation ward",
 "A hybrid model corrects dehydration, hypokalaemia and hypoglycaemia with IV fluids in the first 24 hours before stepping down; outpatient survival is about 80 to 83%. Euthanasia thresholds are BCS under 3/9, recumbency or non-responsiveness, none of which this puppy has."),

("Canine parvovirus", [23, 24, 36],
 "A kennel that housed a puppy with canine parvovirus (CPV) has had organic debris removed. Which disinfection regimen is effective for the cleaned surface?",
 "Accelerated hydrogen peroxide 1:32 with 10 minutes of contact time",
 "Quaternary ammonium compound at label dilution with 10 minutes of contact time",
 "70% alcohol spray with 1 minute of contact time",
 "CPV is a non-enveloped virus. Accelerated hydrogen peroxide (1:32, 10 min), bleach (1:32, 10 min) and 1% potassium peroxymonosulfate (10 min) are effective. Quaternary ammonium compounds and alcohol are unreliable against non-enveloped viruses."),

("Canine parvovirus", [21, 22],
 "During a canine parvovirus (CPV) outbreak, a well 7-month-old dog with no vaccination history shared a run with an affected puppy 3 days ago. What is the most appropriate way to categorise and manage this dog?",
 "Moderate risk; perform antibody titre testing and reclassify if the titre is adequate",
 "High risk; quarantine for 14 days regardless of any test result",
 "Low risk; continue normal adoption without testing because the dog is over 5 months old",
 "Dogs over 5 months with no vaccination history and possible exposure are moderate risk. Titre testing lets protected dogs be reclassified as low risk and placed. Puppies under 5 months are the group that is high risk regardless of history."),

# ---------------- Canine distemper virus (CDV) ----------------
("Canine distemper", [54, 53],
 "An asymptomatic dog received a modified live virus (MLV) distemper vaccine 5 days ago. A nasal swab reverse transcription PCR (RT-PCR) for canine distemper virus (CDV) is positive with a very low cycle threshold (Ct). The most appropriate interpretation is",
 "probable wild-type infection, because a low Ct indicates a high viral load.",
 "vaccine virus shedding, because recent MLV vaccination always produces a positive result.",
 "an uninterpretable result that should be repeated after 6 weeks.",
 "Vaccine virus produces only a low viral load (high Ct). A low Ct (high load) is highly suggestive of active field infection, and a dog with a strongly positive result should be managed as infected."),

("Canine distemper", [73],
 "Which histologic finding best supports a diagnosis of canine distemper in a dog with neurological signs?",
 "Eosinophilic intracytoplasmic and intranuclear inclusions in astrocytes and epithelial cells",
 "Basophilic intranuclear inclusion bodies in hepatocytes and vascular endothelium",
 "Eosinophilic intracytoplasmic Negri bodies in hippocampal neurons",
 "Canine distemper produces both intracytoplasmic and intranuclear eosinophilic inclusions. Intranuclear basophilic inclusions in liver and endothelium suggest canine adenovirus-1, and Negri bodies suggest rabies."),

("Canine distemper", [55, 57, 62],
 "A 9-month-old shelter dog recovered from a mild fever and cough 3 weeks ago. It now has myoclonus and progressive ataxia. The most likely cause is",
 "canine distemper virus neurological disease after resolution of systemic signs.",
 "delayed neurological spread of canine adenovirus-2 infection.",
 "Neospora caninum protozoal encephalitis.",
 "Canine distemper is biphasic and neurological signs can appear 1 to 3 weeks or longer after systemic signs resolve, carrying a poor prognosis. Canine adenovirus-2 causes respiratory rather than neurological disease. Neospora is a differential for neurological signs but the history fits distemper."),

("Canine distemper", [74, 75],
 "Which statement about shedding of canine distemper virus (CDV) after recovery is correct?",
 "There is no true carrier state, but shedding may persist for up to 16 weeks.",
 "Recovered dogs become lifelong carriers that intermittently shed the virus.",
 "Shedding stops within 48 hours of resolution of clinical signs.",
 "CDV has no true carrier state, yet shedding can continue for up to 16 weeks and some dogs remain low-level PCR-positive for months, so they are kept away from susceptible dogs."),

("Canine distemper", [72, 47],
 "In a shelter, several 17-week-old puppies from dams that recovered from field canine distemper virus (CDV) infection fail to respond to modified live virus (MLV) vaccination. The most likely explanation is",
 "persistent high maternal antibody blocking vaccine virus beyond the usual 16 weeks.",
 "a vaccine strain from a different serotype than the field strain.",
 "vaccine-induced immunosuppression from a concurrent parvovirus vaccine.",
 "Very high maternal antibody from dams that recovered from field infection can block MLV past 16 weeks, so shelter series are extended to 20 weeks. CDV has one serotype, so serotype mismatch does not explain vaccine failure."),

# ---------------- Canine infectious respiratory disease (CIRD) / canine influenza ----------------
("Canine respiratory disease", [77, 91, 92],
 "Canine adenovirus-2 differs from canine respiratory coronavirus and canine influenza virus in that it is",
 "non-enveloped, and therefore resistant to alcohol-based sanitisers and quaternary ammonium.",
 "enveloped, and therefore inactivated by quaternary ammonium.",
 "non-enveloped, and therefore reliably inactivated by alcohol-based sanitisers.",
 "Canine adenovirus-2 is the only non-enveloped (DNA) virus among the main respiratory pathogens; it is environmentally stable and resists alcohol and quaternary ammonium. Enveloped agents are susceptible to both."),

("Canine respiratory disease", [84, 85, 87],
 "A shelter dog has fever, lethargy, anorexia and a productive cough. A complete blood count shows leukocytosis with a left shift. These findings are most consistent with",
 "bacterial pneumonia complicating respiratory disease.",
 "uncomplicated viral upper respiratory infection.",
 "a stress leukogram from kennel confinement.",
 "Uncomplicated respiratory disease usually leaves the dog bright and eating with a stress leukogram. Anorexia, fever and an inflammatory leukogram with a left shift indicate lower airway bacterial disease."),

("Canine respiratory disease", [97],
 "A technician accidentally injects an intranasal Bordetella bronchiseptica vaccine subcutaneously. Which outcome should be anticipated?",
 "Cellulitis or abscess at the injection site, with a risk of hepatocellular necrosis",
 "Transient local swelling only, because the vaccine organism is non-viable",
 "Immune-mediated thrombocytopenia within 7 days of injection",
 "Live intranasal Bordetella vaccine given SQ is a significant error: it can cause cellulitis, abscessation and acute hepatocellular necrosis with liver failure, and is treated with doxycycline. The vaccine organism is live."),

("Canine respiratory disease", [86, 103, 104],
 "Several dogs in a kennel die suddenly with haemorrhagic pneumonia within 48 hours of the onset of coughing, and Streptococcus zooepidemicus is cultured. Which antimicrobial is appropriate for the exposed dogs?",
 "A beta-lactam such as penicillin G or cefovecin",
 "Doxycycline 5 mg/kg PO every 12 hours",
 "Azithromycin 10 mg/kg PO once daily",
 "Streptococcus zooepidemicus is resistant to doxycycline and requires a beta-lactam, given prophylactically to exposed dogs because disease is rapid and deadly. Macrolides are reserved for culture-confirmed resistant lower-airway disease."),

("Canine respiratory disease", [123],
 "A human influenza A antigen kit is used on a nasal swab from a coughing dog and the result is negative. Which statement is correct?",
 "The result is uninformative because these kits have poor sensitivity in dogs.",
 "The dog can be released from quarantine because the negative result is reliable.",
 "A positive result would be unreliable, but a negative result reliably excludes canine influenza.",
 "Human antigen kits have poor canine sensitivity. A positive is reliable but a negative cannot clear an animal. Confirmation requires PCR."),

("Canine respiratory disease", [129, 130],
 "Compared with H3N8, isolation of a dog with H3N2 canine influenza virus is longer because",
 "shedding is prolonged and intermittent, so about 21 to 28 days is needed.",
 "H3N2 is spread only by direct contact, so a fixed 14 days is required.",
 "H3N2 produces a persistent lifelong carrier state in recovered dogs.",
 "H3N8 isolation is about 7 to 10 days; H3N2 is about 21 to 28 days because of prolonged intermittent shedding. Neither subtype produces a true carrier state and both spread by aerosol, droplets, contact and fomites."),

("Canine respiratory disease", [131, 133],
 "During an active canine influenza virus outbreak, the manager proposes vaccinating every dog to stop the spread. The best response is",
 "to decline, because the killed vaccine needs two doses 2 to 3 weeks apart before protection.",
 "to agree, because one dose of the vaccine gives protection within 48 hours.",
 "to decline, because the vaccine is contraindicated in dogs already exposed.",
 "The two-dose killed vaccine with delayed protection cannot stop an outbreak already underway; it is also non-core and does not prevent infection. Control depends on isolation, cohorting and sanitation."),

# ---------------- Dermatophytosis ----------------
("Dermatophytosis", [148, 149],
 "A stray kitten with patchy alopecia and scaling is examined with a Wood's lamp and no fluorescence is seen. This finding",
 "does not rule out dermatophytosis, because many infected cats do not fluoresce.",
 "rules out dermatophytosis, so no culture is required.",
 "excludes Microsporum canis, although Trichophyton remains possible.",
 "Only M. canis fluoresces apple-green, and only in about half of cases. A positive is strongly indicative, but a negative never rules out ringworm."),

("Dermatophytosis", [138, 153],
 "A lesion-free cat that is Wood's lamp negative has a dermatophyte test medium (DTM) culture growing Microsporum canis at 2 colony-forming units (CFU). The most appropriate classification and plan is",
 "a fomite (dust-mop) carrier: re-culture, give one lime sulfur dip and proceed to adoption.",
 "an infected cat: begin systemic itraconazole and keep isolated until cured.",
 "a contaminant: disregard the result because M. canis is normal feline flora.",
 "This is a P1 result in a lesion-free cat, consistent with mechanical carriage. Microsporum canis is never normal flora, so every positive needs action, but this action is proportionate (dip-and-go), not full treatment."),

("Dermatophytosis", [156],
 "By day 5, a toothbrush culture plate from a crusted stray cat is fully red and covered in heavy, dark, pigmented, fuzzy colonies. This finding is most consistent with",
 "saprophytic contamination; record as heavy contamination and reculture.",
 "Trichophyton infection; begin treatment immediately.",
 "Microsporum canis infection; begin treatment immediately.",
 "Dermatophytes are typically pale and turn the medium red as they grow. Heavy pigmented overgrowth is saprophytic contamination that can mask true positives, so it is recorded as heavy contamination and re-cultured."),

("Dermatophytosis", [157, 158, 160],
 "Which is the preferred systemic antifungal regimen for a shelter cat with ringworm?",
 "Itraconazole 5 to 10 mg/kg PO once daily for 21 to 28 days, plus lime sulfur",
 "Griseofulvin 25 mg/kg PO twice daily for 6 to 8 weeks, plus lime sulfur",
 "Ketoconazole 10 mg/kg PO once daily for 4 weeks, plus lime sulfur",
 "Itraconazole is preferred. Griseofulvin is avoided (long cure time, teratogenicity, and idiosyncratic irreversible marrow suppression that is potentially lethal in FeLV- or FIV-positive cats). Ketoconazole is poorly tolerated in cats and not a shelter first choice."),

("Dermatophytosis", [163, 164],
 "After hair and debris are mechanically removed from a cat room, which disinfectant is effective against ringworm spores?",
 "2% potassium peroxymonosulfate",
 "1% potassium peroxymonosulfate",
 "Quaternary ammonium at label dilution",
 "Ringworm needs a 2% potassium peroxymonosulfate solution; 1% is unreliable against spores (unlike parvovirus, where 1% works). Quaternary ammonium compounds are ineffective for both."),

("Dermatophytosis", [165],
 "Three cats in one room are being treated for ringworm. Two have had three consecutive negative weekly cultures and the third is still positive. Which is correct?",
 "Hold all three until the third cat also reaches mycological cure.",
 "Release the two negative cats after a final lime sulfur dip.",
 "Release the two negative cats to foster with a repeat culture in 2 weeks.",
 "Co-housed animals are released only when every animal in the group is cured, because a negative cat sharing space with a positive one is re-contaminated."),

# ---------------- Feline panleukopenia virus (FPV) ----------------
("Feline panleukopenia", [169, 177],
 "A litter of 5-week-old kittens has a wide-based stance, hypermetria and intention tremor, with normal mentation. The signs have not progressed. The queen was unvaccinated and had panleukopenia in mid-gestation. The most likely cause of the kittens' signs is",
 "cerebellar hypoplasia from perinatal infection of the cerebellum.",
 "congenital hydrocephalus from obstruction of cerebrospinal fluid flow.",
 "Toxoplasma gondii encephalitis acquired from the queen.",
 "In-utero or perinatal feline panleukopenia virus infection produces non-progressive cerebellar hypoplasia with normal mentation. Progressive signs or altered mentation would point toward hydrocephalus or encephalitis."),

("Feline panleukopenia", [189],
 "An FIV-positive adult cat in a shelter requires protection against feline panleukopenia. Which product is appropriate?",
 "An inactivated feline panleukopenia vaccine",
 "A modified live virus (MLV) FVRCP vaccine, as for other cats",
 "No vaccination, because FIV-positive cats cannot respond to any vaccine",
 "Modified live virus vaccine can precipitate vaccine-induced panleukopenia in immunocompromised cats, so FIV-positive cats receive an inactivated product."),

("Feline panleukopenia", [191],
 "During a feline panleukopenia outbreak, which statement about antibody titre testing to triage exposed cats is correct?",
 "A feline-specific assay is required, because canine kits do not reliably detect feline antibody.",
 "A canine parvovirus antibody kit is a valid substitute, because both viruses share one serotype.",
 "Titre testing is unreliable in cats and should not be used to triage exposed cats.",
 "Canine kits cannot reliably detect FPV antibody in cats. A validated feline-specific assay (haemagglutination inhibition titre of 80 or higher is protective) is used."),

# ---------------- FeLV / FIV ----------------
("FeLV and FIV", [213],
 "A 4-month-old kitten from a stray litter tests positive for feline immunodeficiency virus (FIV) antibody on a point-of-care test. These results indicate",
 "probable maternal antibody; retest at 5 to 6 months of age.",
 "persistent FIV infection; manage as FIV-positive from now on.",
 "prior FIV vaccination; retest with a PCR assay only.",
 "Under 6 months a positive antibody test is almost always maternal antibody (vertical FIV transmission is rare). Retest until 5 to 6 months before calling the kitten infected. FIV vaccination is not recommended in shelters."),

("FeLV and FIV", [198, 199, 200, 211, 212],
 "An adult cat is negative for FeLV p27 antigen on whole blood and negative on immunofluorescent antibody (IFA) testing, but quantitative PCR detects a low proviral copy number. This pattern most likely reflects",
 "regressive infection.",
 "abortive infection.",
 "progressive infection.",
 "Regressive infection features latent provirus in marrow, a negative IFA and a low proviral load. Abortive infection is negative on antigen, IFA and PCR. Progressive infection is generally positive on all three, with a high copy number."),

("FeLV and FIV", [214],
 "A cat is bitten by an FIV-positive cat and shares food dishes with an FeLV-positive cat. Point-of-care tests 10 days later are negative for both. What retest interval is recommended?",
 "FeLV at 30 days and FIV at 60 days after exposure",
 "Both viruses at 14 days after exposure",
 "FeLV at 60 days and FIV at 30 days after exposure",
 "FeLV p27 antigenaemia can take up to 30 days to appear and FIV antibody up to 60 days. Testing earlier can produce false negatives."),

("FeLV and FIV", [215],
 "A healthy unweaned 3-week-old kitten from a stray litter tests positive for FeLV antigen on whole blood at intake. The best management is to",
 "isolate the kitten from unrelated litters and retest at adoption age.",
 "euthanise the kitten to prevent transmission.",
 "place the kitten in foster with unrelated kittens as an FeLV-positive cat.",
 "Many antigen-positive neonates revert as early transient antigenaemia becomes regressive infection, typically within about 16 weeks. A healthy unweaned kitten should not be euthanised on a single intake result, but it should be kept away from unrelated litters."),

("FeLV and FIV", [208],
 "A 2-year-old cat presents with dyspnoea. Radiographs show a cranial mediastinal mass with pleural effusion, and cytology is consistent with T-cell lymphoma. Which underlying infection is most likely?",
 "FeLV infection",
 "FIV infection",
 "Feline coronavirus infection",
 "FeLV classically drives mediastinal (thymic) T-cell lymphoma in young cats. FIV is more associated with B-cell lymphoma (gastrointestinal or nasal) in older cats."),

("FeLV and FIV", [225],
 "A trap-neuter-return programme manager asks whether all trapped community cats should be tested for FeLV and FIV before return. Which advice is best supported?",
 "Routine testing is not recommended; seroprevalence resembles owned cats and sterilisation reduces transmission.",
 "Test all cats and euthanise positives, because returning infected cats endangers the colony.",
 "Test only cats over 6 months of age and vaccinate FeLV-negative cats before return.",
 "Positive cats add no extra threat if they remain outdoors, and resources are better spent on sterilisation, which removes nursing (FeLV) and fight-bite (both) transmission."),

# ---------------- Feline infectious peritonitis (FIP) ----------------
("Feline infectious peritonitis", [235],
 "A 10-month-old cat has a straw-yellow, viscous abdominal effusion with high protein and an albumin:globulin ratio of 0.4. A standard feline coronavirus RT-PCR on the effusion is positive. This result",
 "confirms coronavirus but does not distinguish FIP from enteric coronavirus infection.",
 "confirms FIP, because coronavirus in an effusion is diagnostic of the disease.",
 "is a false positive from faecal contamination and should be disregarded.",
 "Enteric coronavirus can circulate in monocytes and reach extra-intestinal sites, so a positive standard PCR confirms exposure, not mutation to FIPV. The definitive test is antigen within macrophages in pyogranulomatous lesions."),

("Feline infectious peritonitis", [242],
 "Which statement about the Rivalta test on an effusion from a cat suspected of FIP is correct?",
 "It is highly sensitive but poorly specific, so a negative is reassuring while positives occur in other effusions.",
 "It is highly specific but poorly sensitive, so a positive result confirms FIP while a negative does not exclude it.",
 "It has low sensitivity and low specificity, so neither a positive nor a negative result should influence the diagnosis.",
 "Reported Rivalta sensitivity is about 91 to 98% but specificity only about 66 to 80%. A negative lowers suspicion; a positive does not confirm FIP."),

# ---------------- Feline upper respiratory tract disease (URTD) ----------------
("Feline upper respiratory disease", [266, 269],
 "A shelter cat has fever, ulcers on the tongue and hard palate, and lameness that resolves within 48 hours. The most likely pathogen is",
 "feline calicivirus.",
 "feline herpesvirus-1.",
 "Chlamydia felis.",
 "Oral and tongue ulcers and febrile limping syndrome are characteristic of calicivirus. Herpesvirus is associated with dendritic corneal ulcers, and Chlamydia felis with chemosis and conjunctivitis."),

("Feline upper respiratory disease", [270],
 "Several vaccinated cats in one room die within a week, with oedema of the head and paws and cutaneous ulceration, and the disease spreads quickly within the enclosure. The most likely diagnosis is",
 "virulent systemic feline calicivirus.",
 "feline herpesvirus-1 recrudescence.",
 "feline panleukopenia virus infection.",
 "Virulent systemic calicivirus is suspected with high mortality, severe vasculitis with head and paw oedema, and rapid spread; the routine calicivirus vaccine does not reliably protect. Herpesvirus recrudescence does not cause this systemic vasculitis."),

("Feline upper respiratory disease", [272, 273, 274],
 "A shelter cat with acute upper respiratory disease is suspected of Mycoplasma felis and Chlamydia felis infection. Which is the best first-line antibiotic?",
 "Doxycycline, given as a liquid followed by water or food",
 "Amoxicillin, given twice daily with food",
 "Cefovecin, given as a single injection",
 "Mycoplasma has no cell wall, so beta-lactams (amoxicillin, cefovecin) that target peptidoglycan are ineffective; amoxicillin is acceptable only when Mycoplasma and Chlamydia are not suspected. Doxycycline tablets can cause oesophageal strictures, so liquid with a water or food flush is used."),

("Feline upper respiratory disease", [279],
 "A cat vaccinated with an intranasal modified live virus FVRCP vaccine 5 days ago is sneezing. A PCR panel is positive for feline herpesvirus-1 and Mycoplasma felis. The best interpretation is that",
 "the herpesvirus result may reflect vaccine shedding, and Mycoplasma is not proven causal.",
 "both results confirm primary disease from each organism separately.",
 "the herpesvirus result indicates vaccine failure, so revaccination is required.",
 "Intranasal MLV vaccination can cause false-positive herpesvirus and calicivirus PCR results for 1 to 3 weeks, and Mycoplasma is frequently part of normal flora, so PCR does not prove causation."),

("Feline upper respiratory disease", [285, 280],
 "A shelter manager proposes 14-day quarantine for all healthy incoming cats to reduce upper respiratory disease. The best response is",
 "to decline, because a longer stay is the greatest risk factor; vaccinate at intake instead.",
 "to agree, because quarantine before general housing lowers respiratory disease risk.",
 "to modify the plan so that only kittens under 4 months of age are quarantined.",
 "Length of stay is the single greatest URTD risk factor, so routine quarantine of healthy unexposed cats is avoided in favour of intake vaccination, good housing and low length of stay."),

# ---------------- Other infectious disease ----------------
("Other infectious disease", [286, 287],
 "A dog imported from Mexico has a history of late-term abortion. A rapid slide agglutination test for Brucella canis in the clinic is positive. The most appropriate next step is to",
 "isolate the dog and confirm with agar gel immunodiffusion, culture or PCR.",
 "euthanise the dog immediately, because a positive result confirms infection.",
 "spay the dog and begin doxycycline and rifampin without further testing.",
 "The rapid slide agglutination test has a high false-positive rate, so isolation is required but disposition decisions need confirmation. B. canis is zoonotic and not reliably cleared by treatment, so confirmation matters before any treatment or euthanasia decision."),

("Other infectious disease", [289, 290],
 "A 3-year-old FIV-positive cat has severe lethargy, pale mucous membranes, a packed cell volume of 12% and PCR-confirmed Mycoplasma haemofelis infection. Which management is most appropriate?",
 "Doxycycline 10 mg/kg PO once daily for 28 days, with prednisolone if immune-mediated and transfusion if packed cell volume is under 15%",
 "Ronidazole 30 mg/kg PO once daily for 14 days, adding prednisolone and transfusing only if the cat becomes recumbent",
 "Amoxicillin-clavulanate PO for 14 days, with prednisolone started at diagnosis and transfusion only if the cat collapses",
 "Doxycycline is first-line for haemoplasmosis (once daily in cats to reduce oesophageal stricture risk), with prednisolone for an immune-mediated component and transfusion for severe anaemia. Ronidazole is used for Tritrichomonas foetus, and amoxicillin is not effective against a wall-less organism."),

("Other infectious disease", [295],
 "A cluster of kittens has persistent watery diarrhoea and Cryptosporidium oocysts are identified. Which decontamination method is required for the housing?",
 "Steam at 140°F (60°C) or above, or 6% hydrogen peroxide for 30 minutes",
 "Bleach diluted 1:32 with 10 minutes of contact time",
 "Quaternary ammonium compound at label dilution for 10 minutes",
 "Cryptosporidium oocysts resist chlorine disinfectants including standard bleach dilutions. Steam (140°F / 60°C or above) or 6% hydrogen peroxide (30 min) is required, making it one of the hardest pathogens to decontaminate in a shelter."),
]


def balanced_positions(n, k=3, seed=2026):
    """Return n answer positions, as evenly spread over k slots as possible, shuffled."""
    pos = [i % k for i in range(n)]
    random.Random(seed).shuffle(pos)
    return pos


def build(dump_path=None):
    old = {}
    if dump_path:
        for line in pathlib.Path(dump_path).read_text().splitlines():
            m = re.match(r"^(\d+)\|(.*?) ->(.*?) \|\| ", line)
            if m:
                old[int(m.group(1))] = {"q": m.group(2), "a": m.group(3)}
    pos = balanced_positions(len(ITEMS))
    out = []
    for n, (item, p) in enumerate(zip(ITEMS, pos), 1):
        topic, replaces, stem, ok, w1, w2, expl = item
        opts = [w1, w2]
        opts.insert(p, ok)
        out.append({
            "n": n, "topic": topic, "q": stem, "o": opts, "a": p, "e": expl,
            "replaces": [{"idx": i, **old.get(i, {})} for i in replaces],
        })
    return out


if __name__ == "__main__":
    import sys
    dump = sys.argv[1] if len(sys.argv) > 1 else None
    items = build(dump)
    (HERE / "pilot_infectious_disease.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
    from collections import Counter
    print(len(items), "items;", "answer positions:", dict(Counter("abc"[i["a"]] for i in items)))
