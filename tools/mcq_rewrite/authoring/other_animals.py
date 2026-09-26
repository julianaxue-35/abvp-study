import importlib.util, pathlib
PAGE = "physical-health/other-animals_hub.html"

# concepts shared with the Nutrition & Husbandry page reuse the same rewritten item
_nut = importlib.util.spec_from_file_location("nut", pathlib.Path(__file__).with_name("nutrition_husbandry.py"))
_m = importlib.util.module_from_spec(_nut); _nut.loader.exec_module(_m)
def dup(nut_idx, other_idx):
    for it in _m.ITEMS:
        if it[0][0] == nut_idx:
            return ([other_idx],) + tuple(it[1:])
    raise KeyError(nut_idx)

ITEMS = [
# ---- ferrets
dup(61, 0), dup(60, 1), dup(62, 2),

([3],
 "An unbred, unspayed jill (female ferret) in a shelter develops severe non-regenerative anaemia. What is the underlying mechanism?",
 "Ferrets are induced ovulators, so persistent oestrus causes hyperoestrogenism and bone-marrow suppression.",
 "Ferrets have a short luteal phase, so repeated pseudopregnancy depletes iron stores over several months.",
 "Unbred jills develop pyometra in every oestrus cycle, and chronic blood loss then produces anaemia.",
 "An unbred jill stays in oestrus, and chronic hyperoestrogenism causes non-regenerative anaemia and marrow suppression. This is a key reason to spay shelter jills."),

([4],
 "A ferret coronavirus enteritis outbreak is suspected in a shelter. Which statement is correct?",
 "Feline coronavirus PCR will not detect ferret coronavirus; diagnosis needs ferret-specific RT-PCR and immunohistochemistry of the jejunum or ileum.",
 "A feline coronavirus PCR on faeces is diagnostic, because ferret and feline coronaviruses are the same species.",
 "Detection of coronavirus in faeces by RT-PCR alone is confirmatory, since ferrets do not carry it asymptomatically.",
 "Feline coronavirus PCR does not detect ferret coronavirus. Confirmation needs ferret-specific RT-PCR plus immunohistochemistry, because virus presence alone is not confirmatory. Older ferrets often sicken after exposure to young asymptomatic carriers."),

([5],
 "In which US-endemic regions should systemic fungal disease be considered in a ferret with respiratory signs?",
 "Blastomyces in the south-east and Mississippi-Ohio valleys, and Coccidioides in the south-west",
 "Histoplasma in the Pacific north-west, and Cryptococcus in the north-east",
 "Coccidioides in the south-east, and Blastomyces in the Rocky Mountain states",
 "Blastomyces dermatitidis is endemic in the south-east and Mississippi and Ohio river valleys, and Coccidioides immitis in the south-west. They are not contagious between ferrets and are unlikely to arise in a shelter unless exposure occurred earlier."),

([6],
 "A young shelter ferret has chronic mucoid or bloody diarrhoea, thickened intestinal loops and partial rectal prolapse. Which agent, also the cause of hamster wet tail, is most likely?",
 "Lawsonia intracellularis",
 "Clostridium perfringens type A",
 "Helicobacter mustelae",
 "Lawsonia intracellularis causes proliferative bowel disease in young ferrets and is the agent behind wet tail in hamsters. Treatment is chloramphenicol or metronidazole with stress reduction."),

# ---- rabbits
dup(70, 7), dup(71, 8), dup(58, 9),

([10],
 "A shelter is 300 miles (483 km) from an area with rabbit haemorrhagic disease reported last year. Its rabbits are unvaccinated, and a new arrival had outdoor exposure 5 days ago. What applies?",
 "The rabbit is at risk, so it is quarantined for 10 days with risk-mitigation measures.",
 "The rabbit is low risk because it is over 200 miles from the outbreak, so normal intake applies.",
 "The rabbit is at risk only if it shows clinical signs, so it is monitored in general housing.",
 "Within 500 miles (800 km) of recent RHD, an individual risk assessment is done. Outdoor exposure in the last 10 days, an unvaccinated general population or no proof of RHDV2 vaccination each make a rabbit at risk, needing a 10-day quarantine."),

dup(73, 11),

([12],
 "Which set of antibiotics is considered appropriate for routine use in rabbits?",
 "Doxycycline, trimethoprim-sulfonamide and fluoroquinolones",
 "Penicillins, lincomycin and clindamycin given by mouth",
 "Amoxicillin-clavulanate, cephalexin and erythromycin given by mouth",
 "Doxycycline, trimethoprim-sulfa and fluoroquinolones are appropriate. Narrow-spectrum oral antibiotics that target Gram-positive bacteria risk fatal dysbiosis and enterotoxaemia."),

([14],
 "Why is routine spaying recommended for shelter does by 6 to 9 months of age?",
 "About 50 to 80% of intact does develop uterine adenocarcinoma by 3 to 4 years of age.",
 "About 50 to 80% of intact does develop pyometra within a year of their first litter.",
 "Intact does become aggressive at sexual maturity, which makes them unsuitable for adoption.",
 "Uterine adenocarcinoma develops in 50 to 80% of intact does over 3 to 4 years, so ovariohysterectomy is recommended in all non-breeding does at 6 to 9 months."),

# ---- guinea pigs
dup(64, 15), dup(63, 16), dup(66, 17),

([18],
 "A 4-year-old sow guinea pig has bilateral symmetrical truncal alopecia and abdominal distension. Which diagnosis is most likely?",
 "Ovarian cysts, which affect about 76% of guinea pigs by 5 years of age",
 "Trixacarus caviae mange, which affects most older guinea pigs",
 "Hypothyroidism, which is the most common endocrine disease of guinea pigs",
 "About 76% of guinea pigs develop ovarian cysts by 5 years. Space-occupying cysts cause reduced fertility, anorexia, abdominal distension and non-pruritic bilateral truncal alopecia."),

dup(65, 19),

# ---- small rodents
dup(69, 20), dup(68, 21), dup(74, 22),

([23],
 "Which zoonoses are flagged as risks when handling small rodents at a wellness examination?",
 "Hantavirus, lymphocytic choriomeningitis virus and Streptobacillus moniliformis (rat-bite fever)",
 "Leptospira, Salmonella Dublin and Toxoplasma gondii",
 "Rabies virus, Bartonella henselae and Brucella canis",
 "Hantavirus, LCMV and S. moniliformis are the zoonotic risks flagged for small rodents. No routine vaccination or diagnostic testing is done at the wellness examination."),

# ---- reptiles
dup(67, 24),

([25],
 "Which statement about UVB lighting for reptiles is correct?",
 "UVB (290 to 320 nm) must not be filtered through glass or acrylic, should sit 12 to 18 inches (30 to 46 cm) from the animal and the bulb be replaced every 12 months.",
 "UVB passes through glass and acrylic, should be placed 36 inches (91 cm) away and the bulb replaced only when it stops emitting visible light.",
 "UVB is needed only by carnivorous reptiles, so herbivorous species can be housed without it.",
 "UVB (290 to 320 nm) is essential mainly for herbivorous and omnivorous reptiles to make active vitamin D. Glass and acrylic block it, and output declines before visible light does, so bulbs are changed yearly."),

([26],
 "What thermal arrangement do reptiles require in a shelter enclosure?",
 "Ambient 80 to 85°F (27 to 29°C) with a focal heat source about 10°F (5.6°C) warmer, giving a temperature gradient",
 "A uniform 95°F (35°C) throughout the enclosure, so the reptile is never cold",
 "Ambient room temperature with a heat lamp positioned on the floor of the enclosure",
 "Reptiles thermoregulate behaviourally and need a gradient. Too cold causes immunosuppression and gastrointestinal stasis, and too hot causes burns and acute death."),

([27],
 "Which statement is correct for record-keeping and intake of reptiles in a shelter?",
 "Individualise identification and records, mark temporarily with non-toxic paint or nail polish, and review local ownership laws before accepting.",
 "Group reptiles from the same source under one identifier and mark them with a permanent tattoo.",
 "Reptiles can be accepted without review of ownership laws and co-housed with cats to save space.",
 "Records must be individualised, never grouped under one ID. Temporary marks use non-toxic paint or nail polish. Local laws are reviewed first, reptiles are non-social and are not housed with carnivorous mammals, and cat litter must never be used."),

# ---- horses
([28],
 "Which statement about equine squamous gastric ulcer disease is correct?",
 "It affects about 17 to 39% of untrained horses and 66 to 100% of horses in training or competition.",
 "It affects about 66 to 100% of untrained horses and 17 to 39% of horses in training.",
 "It is uncommon in all horses and is seen mainly in foals that are fed concentrates.",
 "Squamous gastric ulcer disease affects about 17 to 39% of untrained horses and 66 to 100% of horses in training or competition, reflecting the effect of management and intermittent feeding on a trickle-feeding species."),

([29],
 "Which pathogens are the priority concern during a 2 to 3 week intake quarantine of rescue horses?",
 "Equine herpesvirus, Salmonella and strangles (Streptococcus equi)",
 "Equine infectious anaemia, West Nile virus and rabies",
 "Tetanus, Potomac horse fever and equine influenza only",
 "Equine herpesvirus and Salmonella have many latently infected shedders stressed by transport, and strangles is common in the auction and holding facilities that rescue horses pass through."),

([30],
 "An orphan foal follows people like a dog, suckles clothing and starts rearing and mounting play with humans. What is this, and how is it managed?",
 "Overhandled foal syndrome: minimise human interaction, bucket-feed rather than bottle-feed, and provide equine companionship.",
 "Normal orphan foal behaviour: increase handling and bottle feeding so that the foal bonds to its carers.",
 "Neonatal maladjustment syndrome: sedate the foal and restrict it to a padded stall for a week.",
 "Overhandled foal syndrome arises when orphan foals over-bond to humans, giving unsafe behaviour and poor trainability. Minimise interaction, bucket-feed using remote filling to dissociate people from mealtime, and provide equine company."),

([31],
 "A shelter horse paces and weaves in its stall. What is the correct interpretation and response?",
 "These are locomotor stereotypies reflecting discomfort and should not be punished; address the cause and provide turn-out and forage.",
 "These are learned vices that should be discouraged with anti-weaving devices and firm handling.",
 "These are signs of colic, so the horse should be walked and given analgesia immediately.",
 "Pacing, circling, weaving and pawing are locomotor stereotypies reflecting physical or psychological discomfort. Management provides continuous forage, turn-out rather than constant stalling, and equine company."),

([32],
 "A horse is chewing wood and licking objects. Which deficiency does this most suggest?",
 "Salt or mineral deficiency",
 "Vitamin E deficiency",
 "Protein deficiency",
 "Wood chewing and object licking suggest salt or mineral deficiency. Horses should have continuous access to an all-forage diet plus salt and trace-mineral licks."),

# ---- birds
([33],
 "Which avian zoonosis is caused by an obligate intracellular bacterium that remains stable in dried droppings for months, so that daily faeces removal is the best control?",
 "Psittacosis (Chlamydia psittaci)",
 "Salmonellosis",
 "Avian tuberculosis (Mycobacterium avium)",
 "Psittacosis is caused by an obligate intracellular bacterium that is stable in dry faeces for months. People are infected mainly by inhaling dried droppings, so daily faeces removal is key. Birds are treated with doxycycline for 45 days."),

([34],
 "A shelter admits a parrot. Which disinfection approach is correct for its respiratory health?",
 "Use an unscented, non-aerosol disinfectant such as dilute bleach, and avoid household odours and aerosols.",
 "Use a scented quaternary ammonium spray, since it leaves no residue on the perches.",
 "Use aerosolised phenolic disinfectants, since they are effective against most avian pathogens.",
 "The avian respiratory tract is highly sensitive. Use an unscented, non-aerosol disinfectant and avoid household odours, aerosols and harsh chemicals."),

([35],
 "Why must intracoelomic fluids be avoided in birds?",
 "Birds lack a diaphragm and their air sacs connect with the lungs, so the fluid can flow into the lungs and drown the bird.",
 "The coelom absorbs fluid too slowly, so it forms a large pocket that compresses the liver.",
 "Bird peritoneal membranes are highly irritant, so the fluid causes fatal peritonitis.",
 "Birds have no diaphragm, and their air sacs communicate with the lungs, so intracoelomic fluid can enter the pulmonary parenchyma. Give fluids orally, subcutaneously or intraosseously."),

([36],
 "In a psittacine, how should organisms cultured from the droppings be interpreted?",
 "Gram-positive flora is normal, while Gram-negative organisms are potential pathogens.",
 "Gram-negative flora is normal, while Gram-positive organisms are potential pathogens.",
 "Any bacterial growth from droppings is abnormal and warrants treatment.",
 "Normal gastrointestinal flora in psittacines is predominantly Gram-positive, so Gram-negative organisms are regarded as potential pathogens."),

([37],
 "What is the most common fungal disease of psittacines, and what is a key preventive measure?",
 "Aspergillosis; clean daily and avoid corncob and walnut-shell bedding",
 "Candidiasis; give oral nystatin to all newly admitted birds",
 "Macrorhabdiosis; add an antifungal to the drinking water weekly",
 "Aspergillosis is a non-contagious soil fungus causing severe respiratory disease after spore inhalation, and its incidence is tied to poor management. Prevent it with daily cleaning and by avoiding corncob and walnut-shell bedding."),

([38],
 "Under the federal Migratory Bird Treaty Act, which birds may be possessed without a USFWS permit?",
 "Pigeons, European starlings, English (house) sparrows and game species",
 "Songbirds under 30 days old, and any bird that is injured",
 "All songbirds, as long as they are held for less than 30 days",
 "The Act prohibits possessing any part of native migratory birds without a USFWS permit. The exceptions are pigeons, European starlings, English (house) sparrows and game species, although state restrictions may apply."),

# ---- wildlife
([39],
 "A wild raccoon is brought to a veterinary clinic. What may the hospital legally do?",
 "Provide emergency care and, in most states, keep the animal about 48 hours before transfer to a permitted rehabilitator.",
 "Keep the raccoon until it recovers and then release it at the site of capture.",
 "Keep it as long as needed for treatment, because a veterinary licence covers wildlife.",
 "A veterinarian may give emergency care, but long-term care needs a state rehabilitator permit, and most states allow possession only about 48 hours. Rabies vector species need a separate permit."),

([40],
 "Which group lists the principal rabies vector species relevant to a shelter, plus the one rodent group of higher concern?",
 "Raccoons, skunks, foxes and bats, plus woodchucks",
 "Raccoons, opossums, squirrels and bats, plus rabbits",
 "Skunks, foxes, chipmunks and bats, plus guinea pigs",
 "Rabies vector species are raccoons, skunks, foxes and bats, and woodchucks are the rodents with notably higher susceptibility. Squirrels, chipmunks, other rodents, rabbits and opossums rarely have rabies."),

([41],
 "A staff member without rabies pre-exposure vaccination offers to examine an infant raccoon, because it is just a baby. What is the correct response?",
 "No one without pre-exposure prophylaxis may handle potential rabies vector species, and age does not affect whether the animal carries the virus.",
 "Allow it with gloves, because infant animals are too young to carry rabies virus.",
 "Allow it if the raccoon has been in captivity for over 10 days without signs.",
 "No staff member may handle wildlife, especially potential rabies vector species, without pre-exposure prophylaxis. An infant raccoon can carry rabies. Always use gloves regardless."),

([42],
 "A caller asks if they can catch rabies from grass that a rabid fox drooled on last night. What is the correct answer?",
 "No; rabies cannot penetrate intact skin, the virus is not viable once saliva dries, and it spreads via saliva entering a bite, fresh wound or mucous membrane.",
 "Yes; rabies virus persists in dried saliva on grass for several days and can be inhaled.",
 "Yes, but only if the person is bitten or scratched by a rodent in the same area.",
 "Rabies cannot penetrate intact skin, and the virus is not viable after saliva dries. It is transmitted by saliva entering a bite wound, fresh abrasion or mucous membrane, not by blood, urine or faeces or the environment."),

([43],
 "Which wildlife zoonosis has roundworm eggs that resist common disinfectants, survive for years, and can be reliably destroyed only by high-heat sterilisation?",
 "Baylisascaris procyonis (raccoon roundworm)",
 "Toxocara canis (canine roundworm)",
 "Echinococcus multilocularis (fox tapeworm)",
 "Baylisascaris eggs are not killed by common disinfectants and survive for years. Only high heat works, such as a propane torch or boiling lye water. In humans the larvae cause neural larva migrans. Cages are designated raccoon-only."),

([44],
 "A fledgling songbird arrives after being caught by a house cat, with no visible wounds. What is the priority?",
 "Start antibiotics such as amoxicillin-clavulanate immediately, assuming invisible puncture wounds and rapid septicaemia.",
 "Withhold antibiotics and monitor for wounds, since none are visible.",
 "Give fluids and warmth only, and start antibiotics if fever develops.",
 "Cat saliva carries highly virulent bacteria, including Pasteurella, that cause rapid fatal septicaemia in small prey. Cat-caught wildlife is started on antibiotics as soon as possible, even without visible wounds."),

([45],
 "An opossum brought in is hissing, drooling and swaying. What does this most likely indicate?",
 "A normal defensive bluff; opossums are remarkably resistant to rabies",
 "Advanced rabies, because opossums are highly susceptible to the virus",
 "Canine distemper, which commonly affects wild opossums",
 "Opossums are remarkably rabies-resistant, and hissing, drooling and swaying are part of their bluff routine. Standard precautions still apply for any wild mammal."),

([46],
 "Under federal migratory bird rules, which finding mandates euthanasia in the absence of special permits?",
 "A bird that cannot feed itself, perch or walk where care will not reverse it, complete blindness, or a wing needing amputation at or above the elbow",
 "A bird with a fractured wing that could heal with splinting and cage rest",
 "A bird with a mild eye injury in one eye that still leaves useful vision",
 "Federal rules require euthanasia of any bird that cannot feed, perch or ambulate where care will not reverse it, any completely blind bird, and any bird needing amputation of a leg, foot or wing at or above the humero-ulnar joint."),
]
