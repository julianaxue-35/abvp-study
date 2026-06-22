#!/usr/bin/env python3
"""
Generate MCQs for g5 batch: 17 records across shelter-management, community-public-health,
behavioral-health, research-biostats, animals-public-policy subdomain pages.
MCQs grounded ONLY in each article's abstract text.
"""

import json
import os

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_PATH = "/Users/jxue/abvp-study/tools/mcqs_partials/g5.json"

# ── Hand-crafted MCQs (grounded strictly in each abstract) ───────────────────
MCQ_MAP = {

    # ── shelter-management/09_resource_allocation.html ────────────────────────
    "2024-survey-of-shelter-medicine-veterinary-compensation": [
        {
            "q": "According to the 2024 Survey of Shelter Medicine Veterinary Compensation, which employment category showed the greatest percentage salary increase compared to 2018?",
            "o": [
                "Full-time clinical shelter veterinarians",
                "Part-time clinical shelter veterinarians",
                "Academic shelter medicine faculty",
                "Veterinarians in consulting or leadership positions"
            ],
            "a": 3,
            "e": "The abstract states that veterinarians in consulting or leadership positions had a 40% salary increase from 2018, the largest of any group. Full-time clinical veterinarians increased 25%, academics 20%, and part-time hourly rate increased 77% but hours decreased."
        },
        {
            "q": "In the 2024 shelter veterinary compensation survey, the median 2024 salary for full-time clinical shelter veterinarians was $122,500. How did this compare to 2022 AVMA-reported salaries for all private practice veterinarians?",
            "o": [
                "5% higher than private practice veterinarians",
                "Equal to private practice veterinarians",
                "5% lower than private practice veterinarians",
                "20% lower than private practice veterinarians"
            ],
            "a": 2,
            "e": "The abstract states that salaries for clinically employed shelter veterinarians were 5% less than AVMA-reported 2022 salaries for all private practice veterinarians (and 7% lower than for companion animal veterinarians)."
        },
        {
            "q": "In the 2024 survey, part-time shelter veterinarians reported which of the following changes compared to 2018?",
            "o": [
                "A 77% increase in hourly wage and working 8% more hours per week",
                "A 77% increase in hourly wage and working 8% fewer hours per week",
                "A 25% increase in hourly wage and no change in hours",
                "A 40% increase in hourly wage and working 2 more hours per week"
            ],
            "a": 1,
            "e": "The abstract reports part-time veterinarians showed a 77% increase in hourly wage (from $48/hr to $85/hr) and an 8% decrease in hours, working a median of 24 hours compared to 26 hours in 2018."
        }
    ],

    # ── shelter-management/07_regulatory.html (retrospective cohort) ──────────
    "a-retrospective-study-of-canine-outcomes-and-length-of-stay-in-a-midwestern-shel": [
        {
            "q": "In the retrospective cohort study of canine outcomes in a shelter subject to breed-specific legislation (BSL), what happened to differences in live versus non-live outcomes when the analysis was restricted to a weight-matched subset?",
            "o": [
                "Legislated dogs remained significantly more likely to be euthanized",
                "Non-legislated dogs became significantly more likely to have non-live outcomes",
                "The significant difference in live versus non-live outcome rates was no longer present",
                "The difference in live outcomes increased significantly in the weight-matched subset"
            ],
            "a": 2,
            "e": "The abstract states that in the weight-matched subset (14.1–30.6 kg), there was no longer a significant difference between groups in the rate of live versus non-live outcomes (X²(1) = 2.022, p = 0.179), though legislated dogs still experienced significantly longer LOS to adoption and return-to-owner."
        },
        {
            "q": "In the same BSL retrospective cohort study, which finding about euthanasia reasons was observed among the 80 dogs whose first outcome was euthanasia?",
            "o": [
                "Legislated dogs were significantly more likely to be euthanized for aggressive behavior",
                "Non-legislated dogs were significantly more likely to be euthanized for medical reasons",
                "There were no differences in euthanasia reasons between legislated and non-legislated dogs",
                "Legislated dogs were significantly more likely to be euthanized for poor quality of life"
            ],
            "a": 1,
            "e": "The abstract states that non-legislated dogs were significantly more likely to be euthanized for medical reasons than legislated dogs, and there were no significant differences in euthanasia for aggressive behavior or behavioral evidence of poor quality of life."
        },
        {
            "q": "Which conclusion did the authors draw about breed-specific legislation (BSL) based on findings from this retrospective cohort study?",
            "o": [
                "BSL is an effective strategy for improving public safety outcomes in managed admission shelters",
                "Overturning BSL would support increased live outcomes, including family reunification, for legislated dogs",
                "BSL primarily increases euthanasia for aggressive behavior in affected breeds",
                "Weight-matching eliminates all disparities between legislated and non-legislated dogs"
            ],
            "a": 1,
            "e": "The abstract concludes that 'overturning BSL would support increased live outcomes, including family reunification, for legislated dogs,' as legislated dogs generally experience barriers to live outcomes."
        }
    ],

    # ── community-public-health/01e_hoarding.html (NYC cat hoarding cases) ────
    "a-retrospective-study-of-cat-hoarding-cases-and-their-management-through-volunta": [
        {
            "q": "In the NYC retrospective study of cat hoarding cases managed through a voluntary spay/neuter and relinquishment program, what proportion of clients showed initial interest in surrender services?",
            "o": [
                "29.1%",
                "41.5%",
                "67.1%",
                "76.0%"
            ],
            "a": 3,
            "e": "The abstract states that at the time of the first interaction with Community Engagement (CE), 76.0% of clients were interested in surrender services, while 88.6% were interested in spay/neuter."
        },
        {
            "q": "According to the NYC cat hoarding retrospective study, which factor was associated with the highest odds ratio for a successful case outcome?",
            "o": [
                "Social service agency involvement at the initial intervention",
                "Client identifying as a rescuer or community cat caregiver",
                "Client's initial interest in surrendering cats",
                "Presence of object hoarding alongside cat hoarding"
            ],
            "a": 2,
            "e": "The abstract states that clients who showed an initial interest in surrender were 10 times more likely (OR 10.0, P = 0.014) to experience a successful outcome than clients not interested in surrender — the highest OR reported."
        },
        {
            "q": "In the NYC cat hoarding study, what was a significant predictor of recidivism (re-collection) following an initially successful case outcome?",
            "o": [
                "Client living alone and high levels of social vulnerability",
                "Client identifying as a rescuer (OR 4.8) or involvement of human service agencies (OR 6.1)",
                "Presence of unsanitary conditions at the time of first contact",
                "Client's initial interest in spay/neuter rather than surrender"
            ],
            "a": 1,
            "e": "The abstract reports that significant predictors of recidivism included clients identifying as rescuers (OR 4.8, P = 0.039) and the involvement of human service agencies during or after the CE intervention (OR 6.1, P = 0.041)."
        }
    ],

    # ── community-public-health/01e_hoarding.html (ASPCA cats from hoarding) ──
    "a-retrospective-descriptive-study-of-medical-conditions-and-outcomes-of-cats-rel": [
        {
            "q": "In the retrospective descriptive study of cats surrendered from hoarding environments to ASPCA sheltering programs, what was the most common medical condition at intake?",
            "o": [
                "Upper respiratory infection (23.8%)",
                "Otitis externa (33.3%)",
                "Dental disease (52.8%)",
                "Dermatophytosis (10.1%)"
            ],
            "a": 2,
            "e": "The abstract states that dental disease was the most common medical condition, present in 52.8% of cats, with 20.3% having moderate to severe disease requiring dentistry procedures."
        },
        {
            "q": "In this ASPCA hoarding study, how did the median length of stay (LOS) for hoarded cats compare to non-hoarded owner/guardian surrendered (OGS) cats?",
            "o": [
                "Hoarded cats had a shorter LOS (28 days vs. 52 days, P < 0.001)",
                "Hoarded cats had a longer LOS (52 days vs. 28 days, P < 0.001)",
                "LOS was similar between hoarded and non-hoarded OGS cats (P = 0.6)",
                "Hoarded cats had a longer LOS only when euthanasia was the outcome"
            ],
            "a": 1,
            "e": "The abstract reports that the median LOS for hoarded cats was 52 days versus 28 days for non-hoarded OGS cats, a significant difference (P < 0.001)."
        },
        {
            "q": "Which intake characteristic was associated with non-live outcomes in hoarded cats in the ASPCA retrospective study?",
            "o": [
                "Presence of ectoparasites at intake",
                "Dermatophytosis (ringworm) diagnosis",
                "Body condition score 1–2 (emaciation) at intake",
                "Behavioral euthanasia due to aggression"
            ],
            "a": 2,
            "e": "The abstract states that body condition score (BCS) 1–2 (emaciation) at intake (P < 0.001), moderate to severe dental disease (P = 0.007), and increased number of medical conditions per cat (P < 0.001) were associated with non-live outcomes."
        }
    ],

    # ── shelter-management/07_regulatory.html (abstract study) ───────────────
    "canine-outcomes-and-length-of-stay-in-a-midwestern-shelter-affected-by-breed-spe": [
        {
            "q": "In this study of canine outcomes in a managed admission shelter subject to BSL, what was found regarding euthanasia for aggressive behavior in legislated versus non-legislated dogs?",
            "o": [
                "Legislated dogs were significantly more likely to be euthanized for aggression",
                "Non-legislated dogs were significantly more likely to be euthanized for aggression",
                "Legislated dogs were not significantly more likely to be euthanized for aggressive behavior",
                "Euthanasia for aggression was equally distributed regardless of BSL status or body weight"
            ],
            "a": 2,
            "e": "The abstract states that Pearson Chi Square testing showed legislated dogs in the euthanasia group were no more likely to be euthanized for aggression than non-legislated dogs — an important finding undermining a key rationale for BSL."
        },
        {
            "q": "In this BSL study, after controlling for body weight, what was found about overall length of stay (LOS) for legislated versus non-legislated dogs in the full population?",
            "o": [
                "LOS remained significantly longer for legislated dogs in all outcome categories",
                "LOS became equivalent between groups overall, although legislated dogs still had longer LOS before live outcomes",
                "LOS became shorter for legislated dogs after weight-adjustment",
                "There was no significant difference in LOS at baseline before weight-adjustment"
            ],
            "a": 1,
            "e": "The abstract states that after controlling for weight, LOS was no longer significantly different for the full study population, though legislated dogs did experience increased LOS before live outcomes (adoption and RTO)."
        }
    ],

    # ── research-biostats/study_design_hub.html ───────────────────────────────
    "finding-yourself-in-the-arena-of-scientific-writing-the-journey-from-idea-to-pub": [
        {
            "q": "According to the article on scientific writing in shelter and community medicine, what are identified as the PRIMARY obstacles to publishing for those in clinical practice?",
            "o": [
                "Insufficient data collection and lack of statistical expertise",
                "Ethical conflicts of interest and limited access to journals",
                "Time, confidence, and lack of familiarity with the structure and style of scientific writing",
                "Absence of mentorship programs and restricted access to research funding"
            ],
            "a": 2,
            "e": "The abstract explicitly states that 'the primary obstacles to publishing are time, confidence, and lack of familiarity or experience with the structure and style of scientific writing.'"
        },
        {
            "q": "The article on scientific writing in shelter medicine asserts that scientific inquiry cannot advance without which of the following?",
            "o": [
                "Randomized controlled trial designs as the gold standard",
                "Clear communication to disseminate findings from reproducible research",
                "Institutional review board approval for all animal studies",
                "Peer-reviewed journal publication in indexed databases"
            ],
            "a": 1,
            "e": "The abstract states 'science cannot advance without clear communication to disseminate findings that result from reproducible research.'"
        },
        {
            "q": "According to the scientific writing article, what can overcome barriers to publication for those in shelter and community medicine?",
            "o": [
                "Access to biostatistical software and formal research training",
                "Collaboration with academic institutions to co-author manuscripts",
                "Graduated exposure, mentoring, patience, and practice",
                "Grant funding and protected research time"
            ],
            "a": 2,
            "e": "The abstract states: 'Such barriers can be overcome through a combination of graduated exposure, mentoring, patience, and practice.'"
        }
    ],

    # ── shelter-management/05_data_analysis.html (Big Data USDA) ─────────────
    "harnessing-big-data-in-the-animal-welfare-industry-utilizing-data-science-to-imp": [
        {
            "q": "In the Big Data study on USDA inspection reports for commercial dog breeding, what were the most prevalent areas of non-compliance revealed by the preliminary analysis?",
            "o": [
                "Inadequate record-keeping and overcrowded housing conditions",
                "Inadequate veterinary care and substandard housing conditions",
                "Failure to report disease outbreaks and improper waste disposal",
                "Lack of socialization programs and inadequate exercise requirements"
            ],
            "a": 1,
            "e": "The abstract states that 'preliminary analysis revealed prevalent areas of non-compliance, such as inadequate veterinary care and substandard housing conditions.'"
        },
        {
            "q": "The Big Data study on commercial dog breeding used data from which time period, and from which type of breeding facility?",
            "o": [
                "2010 to 2020, from Class 'B' research dog facilities",
                "2014 to 2023, from Class 'A' commercial dog breeding facilities",
                "2018 to 2024, from all USDA-licensed dog breeding facilities",
                "2005 to 2023, from Class 'A' and Class 'B' commercial dog facilities"
            ],
            "a": 1,
            "e": "The abstract states the dataset covered 'compliance with animal welfare standards at Class 'A' commercial dog breeding facilities across the United States from 2014 to 2023.'"
        }
    ],

    # ── shelter-management/06_mental_health.html (PROMIS/ProQOL 2023) ─────────
    "measures-of-well-being-in-u-s-animal-shelter-staff-during-2023": [
        {
            "q": "In the 2023 survey of U.S. animal shelter staff well-being using PROMIS and ProQOL instruments, what percentage of respondents had secondary traumatic stress scores in the HIGH range?",
            "o": [
                "49.4%",
                "53.5%",
                "68.0%",
                "90.9%"
            ],
            "a": 3,
            "e": "The abstract reports that 90.9% of shelter staff recorded secondary traumatic stress scores in the high range — the highest of the three ProQOL subscales measured."
        },
        {
            "q": "According to the 2023 well-being survey of U.S. shelter staff, PROMIS scores for anger, anxiety, depression, and fatigue were found to be in what range compared to the general U.S. population?",
            "o": [
                "In the low/normal range, similar to the general U.S. population",
                "In the mild/moderate range, significantly higher than the general U.S. population",
                "In the severe range, significantly higher than the general U.S. population",
                "In the moderate/severe range, significantly lower than the general U.S. population"
            ],
            "a": 1,
            "e": "The abstract states that 'PROMIS results reveal mean anger, anxiety, depression, and fatigue scores in the mild/moderate range, significantly higher than those of the general U.S. population.'"
        },
        {
            "q": "In the 2023 shelter staff well-being survey, what proportion of respondents recorded compassion satisfaction scores in the HIGH range on the ProQOL?",
            "o": [
                "39.1%",
                "49.4%",
                "53.5%",
                "90.9%"
            ],
            "a": 1,
            "e": "The abstract states that 'nearly half of shelter staff respondents (49.4%) recorded compassion satisfaction scores in the high range,' with the remainder in the moderate (39.1%) or low (11.5%) range."
        }
    ],

    # ── shelter-management/05_data_analysis.html (Japan dog intake model) ────
    "model-selection-for-examining-the-association-between-dog-intake-quantity-and-so": [
        {
            "q": "In the Japanese shelter dog intake modeling study, what socioeconomic factor was associated with higher owner-unknown dog intake in urban areas?",
            "o": [
                "Higher proportion of low-income households",
                "Higher proportion of older adult households",
                "Lower education level",
                "Higher proportion of owner-occupied households"
            ],
            "a": 2,
            "e": "The abstract states that in urban areas, higher owner-unknown intake was associated with lower education level (IRR = 0.28 for education, meaning lower education predicted more intake)."
        },
        {
            "q": "In the Japanese dog intake modeling study, what was the primary conclusion regarding intake prevention strategies?",
            "o": [
                "A single national-level policy is sufficient to address all intake types uniformly",
                "Intake prevention strategies may be more effective when tailored to local context and dominant intake pathway",
                "Socioeconomic factors are more important than geographic factors in predicting all types of intake",
                "Owner-relinquished and owner-unknown intakes share the same predictors and require similar strategies"
            ],
            "a": 1,
            "e": "The abstract concludes: 'Supported predictors differed by intake type and administrative setting, suggesting that intake prevention strategies may be more effective when tailored to local context and dominant intake pathway.'"
        }
    ],

    # ── behavioral-health/04_body_language.html ───────────────────────────────
    "online-training-using-an-educational-video-improves-human-ability-to-identify-an": [
        {
            "q": "In the online survey study on kitten fear behavior recognition, what did participants who received the specialized behavior training video show compared to those who received the general kitten care video?",
            "o": [
                "No difference in correct ratings after training, though baseline differed between groups",
                "Significantly greater odds of correctly rating all three kitten fear categories after training",
                "Significantly greater odds of correctly rating moderate fear only, not mild or no-fear categories",
                "Greater accuracy only if they had prior experience with cats before the study"
            ],
            "a": 1,
            "e": "The abstract states that 'participants who received the specialized behavior training had significantly greater odds of being correct after video training for all three categories compared to participants who received the general kitten care video.'"
        },
        {
            "q": "According to the kitten fear behavior study, which additional factors influenced participants' ratings of kitten fear behavior beyond the type of training video received?",
            "o": [
                "Participant age and professional veterinary training",
                "Geographic region and frequency of cat ownership",
                "Previous experience with cats and participant personality",
                "Duration of video clip viewed and number of kittens shown"
            ],
            "a": 2,
            "e": "The abstract states: 'Additionally, previous experience with cats and participant personality impacted ratings,' beyond the effect of the training video type."
        },
        {
            "q": "The kitten fear recognition study classified fear into three severity categories. Which of the following correctly describes these categories?",
            "o": [
                "No fear, mild fear, and severe fear requiring immediate veterinary intervention",
                "No fear requiring no intervention, mild fear requiring awareness of possible intervention, and moderate fear requiring immediate intervention",
                "Latent fear, active fear, and panic requiring sedation",
                "Mild anxiety, moderate anxiety, and severe anxiety with associated aggression"
            ],
            "a": 1,
            "e": "The abstract specifies the three categories as: 'no fear requiring no intervention, mild fear requiring awareness of possible intervention, and moderate fear requiring immediate intervention.'"
        }
    ],

    # ── animals-public-policy/03_legislation.html ─────────────────────────────
    "playing-the-cards-you-are-delt-implementing-feline-lifesaving-programs-and-pract": [
        {
            "q": "In the St. Tammany Parish community case study on feline lifesaving despite restrictive ordinances, what live outcome rate for cats was achieved by December 2023, compared to the starting point in January 2015?",
            "o": [
                "Increased from 50.0% to 80.0%",
                "Increased from 26.4% to 95.4%",
                "Increased from 40.0% to 75.0%",
                "Increased from 10.0% to 60.0%"
            ],
            "a": 1,
            "e": "The abstract states that programs were associated with 'considerable increases in live outcomes for cats (from 26.4 to 95.4%) and corresponding reductions in euthanasia rates (from 71.1 to 3.0%).'"
        },
        {
            "q": "According to the St. Tammany Parish case study, what was the effect of adopting revised ordinance provisions to reduce barriers for community cat management?",
            "o": [
                "The revised provisions were associated with the largest single improvement in feline live outcomes",
                "The provisions resulted in a significant increase in community cat program (CCP) intake",
                "The provisions were associated with relatively little change, though generally positive in removing barriers",
                "The provisions had no measurable effect on feline admissions or outcomes"
            ],
            "a": 2,
            "e": "The abstract states that 'the adoption of revised ordinance provisions to reduce barriers for community cat management was associated with relatively little change; however, these provisions were generally positive in nature, removing an apparent requirement to impound at-large cats and facilitating the operation of a community cat program.'"
        }
    ],

    # ── shelter-management/01_population_management.html ─────────────────────
    "revisiting-pre-mortem-risk-factors-for-mortality-in-kittens-less-than-8-weeks-ol": [
        {
            "q": "In the study reassessing mortality risk factors in underage kittens in a foster care-based program, which clinical sign was associated with the HIGHEST elevated risk of dying?",
            "o": [
                "Diarrhea (almost 3 times greater risk)",
                "Weight loss (6 times greater risk)",
                "Anorexia (15 times greater risk)",
                "Trauma diagnosis (5 times greater risk)"
            ],
            "a": 2,
            "e": "The abstract states that anorexia was associated with a 15 times greater elevated risk of dying — the highest hazard ratio among the clinical signs identified. Lightest weight group was nearly 12 times, weight loss 6 times, trauma 5 times, and diarrhea almost 3 times."
        },
        {
            "q": "The kitten mortality study used which analytical method to identify risk factors associated with death or euthanasia in 595 kittens?",
            "o": [
                "Logistic regression with backwards variable selection",
                "Pearson Chi-Square testing and Mann-Whitney U tests",
                "Cox proportional hazard modeling",
                "Adjusted odds ratios using multivariable linear regression"
            ],
            "a": 2,
            "e": "The abstract states: 'The data were analyzed using Cox proportional hazard modeling with 595 kittens to identify risk factors associated with any death or euthanasia.'"
        }
    ],

    # ── shelter-management/02_animal_id_tracking.html ─────────────────────────
    "tag-you-re-home-reunification-of-pet-cats-with-their-owners-using-a-community-en": [
        {
            "q": "In the Tag! You're Home! Program (TYHP) community case report, what percentage of program enrollees did NOT require shelter intake (i.e., were handled entirely in the community)?",
            "o": [
                "31%",
                "53%",
                "More than 80%",
                "9%"
            ],
            "a": 2,
            "e": "The abstract states: 'Over 80% of TYHP cats did not require shelter intake,' demonstrating the program's effectiveness at keeping cats out of the shelter system."
        },
        {
            "q": "According to the TYHP case report, at what median distance from home were adult stray cats that were returned to their owners through the shelter found?",
            "o": [
                "0.07 km (approximately 0.7 city blocks)",
                "0.27 km (approximately 2.7 city blocks)",
                "2.5 km (approximately 25 city blocks)",
                "1.0 km (approximately 10 city blocks)"
            ],
            "a": 1,
            "e": "The abstract states: 'Cats returned to owners through the shelter were found a median of 0.27 km (interquartile range 0.07–2.5), or approximately 2.7 city blocks, from home.'"
        },
        {
            "q": "The TYHP program enrolled cats meeting which criteria as an alternative to immediate shelter intake?",
            "o": [
                "All stray cats, including kittens and those with identification",
                "Microchipped stray cats only, to expedite owner reunification",
                "Unhealthy or injured cats requiring veterinary triage",
                "Un-microchipped healthy social adult cats"
            ],
            "a": 3,
            "e": "The abstract states the program 'encourages finders to return un-microchipped healthy social adult cats to their neighborhoods with a collar containing the shelter's contact information.'"
        }
    ],

    # ── behavioral-health/09_behaviour_medications.html ──────────────────────
    "the-use-of-psychoactive-medications-and-non-medication-alternatives-for-cats-and": [
        {
            "q": "According to the North American shelter survey on psychoactive medications, which medications were most commonly used for FEARFUL DOGS in shelters?",
            "o": [
                "Gabapentin and fluoxetine",
                "Trazodone and gabapentin",
                "Pheromones and nutraceuticals",
                "Acepromazine and diazepam"
            ],
            "a": 1,
            "e": "The abstract states that 'trazodone and gabapentin were the most commonly used for fearful dogs,' while gabapentin and fluoxetine were most common for fearful cats."
        },
        {
            "q": "In the North American shelter psychoactive medication survey, what were identified as the leading BARRIERS to psychoactive medication administration?",
            "o": [
                "Lack of veterinary oversight and concerns about drug interactions",
                "Cost and uncertainty about the efficacy of treatments",
                "Regulatory restrictions and shortage of approved shelter medications",
                "Staff training requirements and animal handling difficulties"
            ],
            "a": 1,
            "e": "The abstract states: 'Cost and uncertainty about the efficacy of treatments emerged as leading barriers to psychoactive medication administration.'"
        },
        {
            "q": "In this survey of psychoactive medication use in shelters, respondents were asked about non-medication alternatives. Which options were most commonly used?",
            "o": [
                "Behavioral modification programs and environmental enrichment",
                "Pheromones and nutraceuticals",
                "Music therapy and aromatherapy",
                "Towel wraps and low-stress handling alone"
            ],
            "a": 1,
            "e": "The abstract states: 'Pheromones and nutraceuticals were the most commonly used non-medication alternative options.'"
        }
    ],

    # ── shelter-management/03_management_leadership.html (collaborative dynamics) ──
    "unlocking-collaborative-dynamics-exploring-veterinarian-leadership-relationships": [
        {
            "q": "In the study exploring veterinarian-leader collaboration in animal shelters, which group reported the HIGHEST positive attitudes toward veterinarian-leader relationship effectiveness (ATVLRE)?",
            "o": [
                "Veterinarian non-leaders (M = 3.1)",
                "Veterinarian leaders (M = 3.7)",
                "Non-veterinarian leaders (M = 4.0)",
                "All groups reported equivalent ATVLRE scores"
            ],
            "a": 2,
            "e": "The abstract states: 'Non-veterinarian leaders reported the highest positive ATVLRE (M = 4.0, SD = 0.6), followed by veterinarian leaders (M = 3.7) and veterinarian non-leaders (M = 3.1).'"
        },
        {
            "q": "According to the shelter veterinarian-leader collaboration study, what was the most reported challenge specifically for VETERINARIAN NON-LEADERS?",
            "o": [
                "Differences in priorities or conflicting goals",
                "Managing expectations and demands",
                "Lack of effective communication",
                "Insufficient resources for medical care"
            ],
            "a": 2,
            "e": "The abstract states that the most reported challenge for veterinarian non-leaders was 'lack of effective communication' (70%; n = 31/44), compared to the other groups whose top challenges differed."
        },
        {
            "q": "In the veterinarian-leader collaboration study, what was identified as the primary contributor to SUCCESSFUL RELATIONSHIPS across ALL groups?",
            "o": [
                "Shared financial decision-making authority",
                "Clearly defined roles and organizational hierarchy",
                "Communication",
                "Alignment on euthanasia decision-making processes"
            ],
            "a": 2,
            "e": "The abstract states: 'Communication was the primary contributor to successful relationships across all groups (68%; n = 122/179).'"
        }
    ],

    # ── shelter-management/03_management_leadership.html (VoRR) ──────────────
    "veterinarian-of-record-relationships-for-animal-shelters-differences-in-expectat": [
        {
            "q": "In the study on Veterinarian of Record Relationships (VoRRs) for animal shelters, what was the PRIMARY legal concern more frequently reported by VETERINARIANS than by nonveterinarian administrators?",
            "o": [
                "Liability for negligent medical decisions made by shelter staff",
                "Adherence to legal requirements to fulfill a veterinary-client-patient relationship (VCPR)",
                "State licensing board restrictions on telepharmacy dispensing",
                "Controlled substance regulations for drug ordering and storage"
            ],
            "a": 1,
            "e": "The abstract states: 'Veterinarians were significantly more concerned than nonveterinarian administrators about adherence to the legal requirements to fulfill a veterinary-client-patient relationship (VCPR).'"
        },
        {
            "q": "Which finding about compensation expectations was identified in the VoRR study between veterinarians and shelter administrators?",
            "o": [
                "Shelter administrators expected to pay more than veterinarians demanded for VoR services",
                "Veterinarians expected significantly higher compensation for services than shelter administrators expected to provide",
                "Both groups agreed on compensation but disagreed on the scope of services",
                "There was no significant difference in compensation expectations between the two groups"
            ],
            "a": 1,
            "e": "The abstract states: 'Veterinarians expected significantly higher compensation for veterinary services than shelter administrators expected to provide,' suggesting a financial disconnect in VoRR expectations."
        }
    ],

    # ── shelter-management/06_mental_health.html (ACEs study) ────────────────
    "i-m-tired-in-my-bones-associations-between-adverse-childhood-experiences-seconda": [
        {
            "q": "In the study examining ACEs and secondary traumatic stress in animal shelter workers (ASW) in Tennessee, what proportion of ASWs had an ACEs score of 4 or greater?",
            "o": [
                "Approximately 5–10% (similar to the general population)",
                "Approximately 25%",
                "Over 50%",
                "Approximately 40%"
            ],
            "a": 2,
            "e": "The abstract states: 'Over 50% of the ASWs had an ACEs score of 4 or greater,' compared to an estimated 5–10% in the general population — indicating a substantially elevated rate of adverse childhood experiences."
        },
        {
            "q": "According to the ACEs and shelter worker study, as ACEs score increased, what pattern was observed in methods of emotional co-regulation?",
            "o": [
                "Reliance on professional mental health services increased significantly",
                "Use of friends and family for emotional co-regulation decreased",
                "Reliance on pets for co-regulation decreased significantly",
                "Both professional support and peer support decreased equally"
            ],
            "a": 1,
            "e": "The abstract states: 'As ACEs score increased, use of friends and family for emotional co-regulation decreased (both r = -0.2 and P = 0.006 and 0.023, respectively),' suggesting a shift toward other sources such as pets."
        },
        {
            "q": "In the ACEs study of animal shelter workers, which ProQOL measure was NOT significantly correlated with ACEs score?",
            "o": [
                "Burnout",
                "Secondary traumatic stress",
                "Compassion satisfaction",
                "Trauma subscale"
            ],
            "a": 2,
            "e": "The abstract reports that ACEs were correlated with burnout (r = 0.3) and trauma (r = 0.4), but NOT with compassion satisfaction (r = -0.1, p = 0.433)."
        }
    ]
}

# ── Verify and write output ────────────────────────────────────────────────────

def verify_mcqs(mcq_map):
    errors = []
    for rid, mcqs in mcq_map.items():
        for i, mcq in enumerate(mcqs):
            if len(mcq["o"]) != 4:
                errors.append(f"{rid}[{i}]: expected 4 options, got {len(mcq['o'])}")
            if not (0 <= mcq["a"] <= 3):
                errors.append(f"{rid}[{i}]: answer index {mcq['a']} out of range 0..3")
            for k in ("q", "o", "a", "e"):
                if k not in mcq:
                    errors.append(f"{rid}[{i}]: missing key '{k}'")
    return errors

errors = verify_mcqs(MCQ_MAP)
if errors:
    print("ERRORS FOUND:")
    for e in errors:
        print(f"  {e}")
else:
    print("All MCQs pass validation (4 options, a in 0..3, all keys present).")

total_records = len(MCQ_MAP)
total_mcqs = sum(len(v) for v in MCQ_MAP.values())
print(f"\nProcessed {total_records} records, {total_mcqs} MCQs total.")
for rid, mcqs in MCQ_MAP.items():
    print(f"  {rid}: {len(mcqs)} MCQs")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(MCQ_MAP, f, ensure_ascii=False, indent=2)

print(f"\nWritten to {OUTPUT_PATH}")

# Sanity-read back
with open(OUTPUT_PATH) as f:
    check = json.load(f)
print(f"Re-read OK: {len(check)} IDs in output file.")
