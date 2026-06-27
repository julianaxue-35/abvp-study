export const meta = {
  name: 'discovery-2025-2026',
  description: 'Find NEW 2025-2026 shelter-med articles: per-diplomate + topic sweeps (real abstracts, written to partials)',
  phases: [{ title: 'Diplomates' }, { title: 'Topics' }],
}
const DIP_GROUPS = [["Aimee Dalrymple", "Alexandra Protopopova", "Alexandre Ellis", "Amanda Dykstra", "Amie Burling"], ["Barbara Laderman-Jones", "Biana Tamimi", "Bonnie Yoffe-Sharp", "Brenda Dines", "Brenda Griffin"], ["Brian DiGangi", "Chelsea Reinhard", "Chumkee Aziz", "Claudia J Baldwin", "Cynthia Cox"], ["Cynthia Karsten", "Elise Gingrich", "Elizabeth Berliner", "Emilia Gordon", "Emily Ferrell"], ["Erin Doyle", "Gary J Patronek", "Jacqueline Harter", "Janet M Scarlett", "Jeanette O'Quin"], ["Jessica Thiele", "Julie Levy", "Jyothi Robertson", "Kate Hurley", "Katheleen Makolinski"], ["Katherine Polak", "Kris Otteman", "Laura Bunke", "Lena DeTar", "Lesli Groshong"], ["Lila Miller", "Lisa Rodriguez", "Martha Smith-Blackmore", "Melinda D Merck", "Michael R Lappin"], ["Miranda Spindel", "Nancy Bradley-Siemens", "Philip A Bushby", "Rebecca Rhodes", "Rebecca Stuntebeck"], ["Sandra Newbury", "Shelia D'Arpino Segurson", "Staci Cannon", "Stephanie Janeczko", "Uri Donnett"], ["Victry Fredley", "Zarah Hedge"]];
const TOPICS = [{"label": "id", "tab": "Infectious Disease", "theme": "shelter/companion-animal INFECTIOUS DISEASE \u2014 canine parvovirus, panleukopenia, FIP/FCoV, feline & canine URI/CIRDC, dermatophytosis/ringworm, FeLV/FIV, leptospirosis, influenza, vaccination, diagnostics, outbreak management, biosecurity/sanitation, parasites/heartworm"}, {"label": "behaviour", "tab": "Behaviour", "theme": "shelter dog and cat BEHAVIOUR & WELFARE \u2014 behavioural assessment, fear/stress/arousal, enrichment, training/behaviour modification, playgroups, psychopharmacology/behaviour medications, quality of life, human-animal interaction"}, {"label": "misc_spayneuter", "tab": "Misc", "theme": "spay/neuter & POPULATION \u2014 HQHVSN, surgical sterilization techniques, non-surgical contraception, TNR/return-to-field, community cats, age at sterilization, population management/modelling"}, {"label": "misc_adoption", "tab": "Misc", "theme": "ADOPTION & OUTCOMES \u2014 adoption, length of stay, foster care, return-to-owner/reunification, post-adoption behaviour, intake-to-outcome, capacity for care, live release"}, {"label": "misc_access", "tab": "Misc", "theme": "ACCESS TO VETERINARY CARE & PUBLIC HEALTH \u2014 community/accessible veterinary care, subsidised care, One Health, zoonoses, rabies, antimicrobial resistance, human-animal bond, social determinants"}, {"label": "misc_forensics", "tab": "Misc", "theme": "VETERINARY FORENSICS & CRUELTY \u2014 animal cruelty, neglect, hoarding, animal fighting, forensic pathology, welfare assessment, law/policy"}, {"label": "misc_mgmt", "tab": "Misc", "theme": "SHELTER MANAGEMENT & DATA \u2014 capacity for care, intake/diversion, transport/relocation, disaster response, data analysis/biostatistics, staff wellbeing/mental health, leadership"}, {"label": "misc_surgmed", "tab": "Misc", "theme": "SHELTER SURGERY, ANAESTHESIA & GENERAL MEDICINE \u2014 anaesthesia/analgesia protocols, pain, pediatrics/neonatology, nutrition, euthanasia, general medical conditions, small mammals/exotics in shelters"}];
const CAND_SCHEMA = { type:'object', required:['candidates'], properties:{ candidates:{ type:'array', items:{
  type:'object', required:['diplomate','authors','title','journal','year','abstract','takeaways','topic_tab','source_url'],
  properties:{ diplomate:{type:'string'}, authors:{type:'string'}, title:{type:'string'}, journal:{type:'string'},
    year:{type:'integer'}, abstract:{type:'string'}, takeaways:{type:'string'}, topic_tab:{type:'string'}, source_url:{type:'string'} } } } } };
const WRITE_SCHEMA = { type:'object', required:['written','file'], properties:{ written:{type:'integer'}, file:{type:'string'} } };

const NOFAB = "Only include articles you can VERIFY exist via a real source URL (PubMed/DOI/journal page); fetch the REAL abstract text. DO NOT fabricate articles, authors, or abstracts. Year MUST be 2025 or 2026 only.";

phase('Diplomates');
const dip = await parallel(DIP_GROUPS.map((grp, i) => () => agent(
  `Find 2025-2026 journal publications by these ABVP Shelter Medicine diplomates: ${grp.join('; ')}.
For EACH name, search PubMed (pubmed.ncbi.nlm.nih.gov), Google Scholar, and journal sites for journal articles published in 2025 or 2026 with that person as an author (any author position). ${NOFAB}
For each verified article return an object: {diplomate:"<which roster name>", authors:"<full author list>", title, journal, year, abstract:"<real abstract>", takeaways:"<1-2 exam-relevant points>", topic_tab:"Diplomate Publications", source_url:"<pubmed/doi/journal URL>"}.
Collect all into an array and WRITE it (even if empty: []) to \`tools/discovery_2025_2026/cand_dip_${i}.json\` using your Write tool. Return {written:<count>, file:"tools/discovery_2025_2026/cand_dip_${i}.json"}.`,
  { label: `dip:${i}`, phase: 'Diplomates', schema: WRITE_SCHEMA }
)));

phase('Topics');
const top = await parallel(TOPICS.map((t, i) => () => agent(
  `Find NEW shelter/community animal-health journal articles published in 2025 or 2026 on this theme: ${t.theme}.
Search PubMed, Google Scholar, and key journals: Journal of Shelter Medicine and Community Animal Health (JSMCAH), JFMS, JAVMA, AJVR, JSAP, Animals (MDPI), Frontiers in Veterinary Science, Veterinary Record, Preventive Veterinary Medicine, JAAWS, Topics in Companion Animal Medicine. ${NOFAB}
Aim for breadth (15+ articles if available). For each: {diplomate:"<author name IF one is an ABVP shelter-med diplomate, else empty string>", authors, title, journal, year, abstract:"<real abstract>", takeaways:"<1-2 exam-relevant points>", topic_tab:"${t.tab}", source_url:"<URL>"}.
WRITE the array to \`tools/discovery_2025_2026/cand_topic_${i}.json\` using your Write tool. Return {written:<count>, file:"tools/discovery_2025_2026/cand_topic_${i}.json"}.`,
  { label: `topic:${t.label}`, phase: 'Topics', schema: WRITE_SCHEMA }
)));

const ok = [...dip, ...top].filter(Boolean);
log(`discovery wrote ${ok.length} partial files (${DIP_GROUPS.length} diplomate groups + ${TOPICS.length} topic sweeps)`);
return { partials: ok };

