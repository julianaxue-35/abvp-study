#!/usr/bin/env python3
"""Classify a journal string against the 23 ABVP-listed journals + the core journal.

Three outcomes, deliberately:
  on_list(j)  -> True for a listed journal, including the abbreviations used in
                 the legacy board-review sheets ("JAAWS", "Frontiers", "Vet Journal").
  off_list(j) -> True only for a journal positively identified as NOT listed.
  neither     -> unrecognised (author names that leaked into the journal column,
                 typos we cannot resolve). Left alone rather than moved on a guess.

Matching is strict by design. Loose subset matching wrongly accepted
"Reproduction in Domestic Animals" (via the single-word canonical "Animals")
and "Veterinary Sciences" (via "Frontiers in Veterinary Science").
"""
import re

# canonical listed journals, normalised
CANON = {
    "journal of shelter medicine and community animal health",
    "animal welfare",
    "animals",
    "anthrozoos",
    "applied animal behaviour science",
    "emerging infectious diseases",
    "forensic science international reports",
    "frontiers in veterinary science",
    "journal of the american veterinary medical association",
    "journal of applied animal welfare science",
    "journal of feline medicine and surgery",
    "journal of forensic sciences",
    "journal of veterinary behaviour",
    "journal of veterinary internal medicine",
    "journal of veterinary medical education",
    "plos one",
    "preventive veterinary medicine",
    "veterinary dermatology",
    "veterinary journal",
    "veterinary microbiology",
    "veterinary parasitology",
    "veterinary pathology",
    "veterinary record",
    "zoonoses and public health",
}

# acronyms that stand for a listed journal; matched as a whole word anywhere
ACRONYM = {
    "jaaws", "javma", "jvme", "jvim", "jfms", "jsmcah", "jvb", "jaabs",
    "plosone", "eid", "vetrecord", "aabs",
}

EXPAND = {
    "j": "journal", "jnl": "journal", "jour": "journal",
    "vet": "veterinary", "veterinar": "veterinary", "veterinay": "veterinary",
    "sci": "science", "scien": "science", "scis": "science",
    "behav": "behaviour", "behavior": "behaviour", "behavioural": "behaviour",
    "behavioral": "behaviour", "beh": "behaviour", "behaviour": "behaviour",
    "anim": "animal", "an": "animal", "anima": "animal", "amimal": "animal",
    "app": "applied", "appl": "applied",
    "med": "medicine", "medical": "medicine", "medicines": "medicine",
    "surg": "surgery", "assoc": "association", "amer": "american", "am": "american",
    "educ": "education", "prev": "preventive", "prevent": "preventive",
    "microbiol": "microbiology", "parasitol": "parasitology",
    "pathol": "pathology", "path": "pathology",
    "derm": "dermatology", "dermatol": "dermatology",
    "forens": "forensic", "welf": "welfare",
    "ph": "public health", "publ": "public", "hlth": "health",
    "rec": "record", "front": "frontiers", "zoonosis": "zoonoses",
    "comm": "community", "fel": "feline", "felin": "feline",
    "internal": "internal", "int": "internal",
}
STOP = {"the", "of", "and", "in", "for", "a", "an", "on", "&", "open", "reports",
        "basel", "mdpi", "switzerland", "online", "early", "view"}


PUBLISHER = ("mdpi", "basel", "switzerland", "online")


def _flat(j):
    s = " ".join(re.sub(r"[^a-z0-9 ]", " ", str(j or "").lower()).split())
    words = [w for w in s.split() if w not in PUBLISHER]
    # drop a stray single leading letter ("S Frontiers", "L Journal of Animals")
    while len(words) > 1 and len(words[0]) == 1 and words[0] != "j":
        words = words[1:]
    return " ".join(words)


# variants that resolve to a listed journal but are too irregular for the rules
ON_ALIAS = {
    "animals", "animal", "journal of animals", "journal animals",
    "anthroozoos", "anthrozoos", "anthrozoos journal",
    "plos one", "plos 1", "plosone",
}


def _tok(j):
    s = re.sub(r"\(.*?\)", " ", str(j or "").lower())
    s = re.sub(r"[^a-z0-9]+", " ", s)
    parts = [p for p in s.split() if p]
    # strip a stray single leading letter ("L Journal of Animals")
    while len(parts) > 1 and len(parts[0]) == 1 and parts[0] != "j":
        parts = parts[1:]
    out = []
    for p in parts:
        if p in STOP:
            continue
        e = EXPAND.get(p, p)
        out.extend(e.split())
    # singular form of each token, so "diseases"/"disease" both match
    return {w[:-1] if len(w) > 4 and w.endswith("s") else w for w in out}


_CANON = {c: _tok(c) for c in CANON}
# Canonicals excluded from the abbreviation rule. The short ones ("animals")
# would swallow any title containing that word; "frontiers in veterinary
# science" would swallow the separate journal "Veterinary Sciences", so
# Frontiers titles are resolved by their own branch instead.
_SHORT = {"animals", "anthrozoos", "plos one", "frontiers in veterinary science"}

FRONTIERS_VET_OK = ("veterinary", "vet med", "vet sci")
FRONTIERS_OTHER = ("psych", "conservation", "cellular", "immunol", "microbiol",
                   "nutrition", "genetic", "ecology", "public health", "sustain")

OFF_LIST = {
    "pathogens", "pets", "vaccines", "scientific reports", "nature communications",
    "journal of primary care community health", "veterinary medicine international",
    "iscience", "bmc veterinary research", "bmc vet res", "viruses",
    "veterinary ophthalmology", "veterinary opthamology", "vet ophthalmology",
    "journal of small animal practice", "jsap", "transboundary emerging disease",
    "transbound emerg disease", "veterinary research", "vet research",
    "parasites vectors", "parasit vectors", "parasites and vectors",
    "perspectives in legal and forensic sciences",
    "plos neglected tropical diseases", "peerj", "peer j", "veterinary world",
    "veterinary clinics of north america", "vet clinics na",
    "veterinary anaesthesia and analgesia", "physiology behavior",
    "american journal of public health", "folia primatologica",
    "trends in parasitology", "advances in parasitology",
    "epidemiology and infection", "jvecc",
    "journal of veterinary emergency and critical care",
    "american journal of veterinary research", "ajvr",
    "journal of the american animal hospital association", "jaaha",
    "reproduction in domestic animals", "veterinary sciences",
    "topics in companion animal medicine", "journal small animal practice",
    "small animal practice", "j small anim pract",
    "frontiers in psych", "frontiers in psychology",
    "frontiers in conservation science",
    "frontiers in cellular and infection microbiology",
}


def on_list(journal):
    raw = _flat(journal)
    if not raw:
        return False
    if raw in ON_ALIAS:
        return True
    words = set(raw.split())
    if words & ACRONYM:
        return True
    if "frontiers" in words:
        if any(k in raw for k in FRONTIERS_OTHER):
            return False
        # bare "Frontiers" in these sheets means Frontiers in Veterinary Science
        return len(words - {"frontiers"}) == 0 or any(k in raw for k in FRONTIERS_VET_OK)
    if raw.startswith("zoonose") or raw.startswith("zoonosi"):
        return True
    # an explicitly known off-list title never counts as on-list
    if raw in OFF_LIST:
        return False
    t = _tok(journal)
    if not t:
        return False
    for c, ct in _CANON.items():
        if t == ct:
            return True
        if c in _SHORT:
            continue                      # "animals" only matches exactly
        # candidate contains the whole canonical title and little else
        if ct <= t and len(t) - len(ct) <= 1:
            return True
        # candidate is an abbreviation of the canonical: strict subset, and it
        # must carry all but one of the canonical's significant words
        if t < ct and len(t) >= len(ct) - 1 and len(ct) >= 3:
            return True
    return False


def off_list(journal):
    if on_list(journal):
        return False
    raw = _flat(journal)
    if len(raw) < 4:
        return False
    if raw in OFF_LIST:
        return True
    return any(raw.startswith(o) or o.startswith(raw) for o in OFF_LIST if len(raw) > 5)
