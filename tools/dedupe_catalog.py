#!/usr/bin/env python3
"""dedupe_catalog.py — merge catalog entries that describe the same article.

Some papers were extracted twice (e.g. the full PDF and the JSMCAH
"[Abstract]" page), producing two entries for one article. Each copy carries
its own distinct MCQs, so the mock exam was drawing from both — harmless in
itself, but it makes MCQ counts per article misleading and lets edits land on
whichever copy you happen to find first, which is how the dual-unit wording
ended up on one copy of the castration question and not the other.

Only pairs on the SAME subdomain_page are merged. Where the two copies sit on
different pages, the split may be a deliberate cross-listing of one paper onto
two relevant hubs — merging would silently drop the article from one of them —
so those are reported and left alone.

Survivor = the copy with a DOI, then the longer abstract. MCQs are unioned
(near-duplicates within 0.85 are collapsed, keeping the longer wording, which
is what the dual-unit pass produces).

Usage:
    python3 tools/dedupe_catalog.py --dry
    python3 tools/dedupe_catalog.py
"""
import argparse
import collections
import difflib
import json
import re
import sys
from pathlib import Path

CATALOG = Path(__file__).resolve().parent / "journal-catalog.json"


def norm(title):
    t = re.sub(r"\[abstract\].*$", "", title.lower())
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


# Companion papers are often titled identically except for one contrastive
# word, and score well above any sensible similarity threshold:
#   "…outcomes for bitches with pyometra" / "…for queens with pyometra"
#   "Welfare and quality of life assessments for shelter dogs / … cats"
#   "…animal sheltering and protection I / II"
# Merging those would delete a real article and pool two papers' questions
# into one entry, so a title pair differing by any of these is never a match.
CONTRAST = {
    "cat", "cats", "feline", "felines", "kitten", "kittens", "queen", "queens",
    "dog", "dogs", "canine", "canines", "puppy", "puppies", "bitch", "bitches",
    "male", "males", "female", "females", "i", "ii", "iii", "iv", "one", "two",
    "first", "second", "adult", "adults", "juvenile", "juveniles",
}


def contrastive(k1, k2):
    diff = set(k1.split()) ^ set(k2.split())
    return bool(diff & CONTRAST)


def groups(cat):
    """Same-article candidate groups, keyed by normalised title."""
    g = collections.defaultdict(list)
    for a in cat:
        g[norm(a["title"])].append(a)
    out = [v for v in g.values() if len(v) > 1]
    # near-identical titles that differ by a typo or "versus"/"vs"
    keys = sorted(g)
    for i, k in enumerate(keys):
        for k2 in keys[i + 1:]:
            if k[:28] != k2[:28] or abs(len(k) - len(k2)) > 12:
                continue
            if difflib.SequenceMatcher(None, k, k2).ratio() < 0.92:
                continue
            if contrastive(k, k2):
                print(f"  KEEP  distinct papers (differ by species/number): "
                      f"{g[k][0]['title'][:52]}")
                continue
            out.append(g[k] + g[k2])
    return out


def merge_mcqs(entries):
    kept = []
    for a in entries:
        for m in a.get("mcqs") or []:
            dup = next(
                (k for k in kept
                 if difflib.SequenceMatcher(None, k["q"], m["q"]).ratio() >= 0.85),
                None,
            )
            if dup is None:
                kept.append(m)
            elif len(m["q"]) > len(dup["q"]):     # prefer the dual-unit wording
                kept[kept.index(dup)] = m
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    merged = skipped = 0
    drop = []

    for grp in groups(cat):
        pages = {a["subdomain_page"] for a in grp}
        if len(pages) > 1:
            skipped += 1
            print(f"  SKIP (cross-listed on {len(pages)} pages) {grp[0]['title'][:58]}")
            for a in grp:
                print(f"        {a['subdomain_page']}  mcqs={len(a.get('mcqs') or [])}  {a['year']}")
            continue
        survivor = sorted(
            grp, key=lambda a: (bool(a.get("doi")), len(a.get("abstract") or "")), reverse=True
        )[0]
        others = [a for a in grp if a is not survivor]
        before = sum(len(a.get("mcqs") or []) for a in grp)
        pooled = merge_mcqs([survivor] + others)
        print(f"  MERGE {survivor['title'][:62]}")
        print(f"        kept {survivor['year']} (abs {len(survivor.get('abstract') or '')}ch, "
              f"doi={bool(survivor.get('doi'))}); MCQs {before} -> {len(pooled)}")
        if not args.dry:
            survivor["mcqs"] = pooled
            drop.extend(id(a) for a in others)
        merged += 1

    if not args.dry and drop:
        cat = [a for a in cat if id(a) not in set(drop)]
        CATALOG.write_text(json.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'would merge' if args.dry else 'merged'} {merged} group(s); "
          f"{skipped} cross-listed group(s) left alone; catalog {len(cat)} entries")


if __name__ == "__main__":
    sys.exit(main())
