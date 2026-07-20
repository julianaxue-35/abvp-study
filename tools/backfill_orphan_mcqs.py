#!/usr/bin/env python3
"""backfill_orphan_mcqs.py — one-off: give the orphaned mock-exam MCQs a home.

mock-data-journal.js had drifted ahead of journal-catalog.json: a set of
questions existed only in the generated file, with no backing article, so any
rebuild dropped them silently. Their source articles were still recoverable
from tools/shards/** (the folder/discovery extraction stage), which carries
real title/authors/journal/year/abstract — so the catalog entries below are
built from that captured metadata, not invented.

Run once, then `python3 tools/build_mock_journal.py --prune`.
"""
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
CATALOG = TOOLS / "journal-catalog.json"

# orphan index -> shard title prefix (None = attach to an existing catalog entry)
GROUPS = [
    ("Prevalence, diagnosis, and manifestations of brucellosis",
     [3, 4, 5], "physical-health/infectious_disease_hub.html"),
    ("A review of evidence-based management of infectious ocular surface disease",
     [6, 7, 8], "physical-health/infectious_disease_hub.html"),
    ("Lessons and Recommendations from a Pentobarbital Shortage",
     [9, 10, 11], "physical-health/euthanasia_hub.html"),
    ("International Renal Interest Society best practice consensus guidelines",
     [12, 13], "physical-health/medical_health_hub.html"),
    ("Environmental risk factors in puppies and kittens",
     [14, 15, 16], "physical-health/nutrition_husbandry_hub.html"),
    ("Resistance of companion animal parasites to antiparasitic drugs",
     [17, 18], "physical-health/parasites_hub.html"),
    ("Feline vector-borne diseases: from local risks to global concerns",
     [19, 20, 21], "physical-health/parasites_hub.html"),
]

# orphan index -> exact title of an article already in the catalog
ATTACH = {0: "Evaluation of Autoligation of the Spermatic Cord for Castration of Small Adult Dogs"}

# Stems that do not stand on their own once shuffled into the mock exam.
# "The article's main recommendations focus on what?" is unanswerable when the
# article is not on screen. Options and correct index are untouched.
RESTEM = {
    9: "In a review of the 2021 pentobarbital shortage in the US and Canada, "
       "how is pentobarbital sodium characterised for companion-animal euthanasia?",
    11: "A review of the 2021 US and Canadian pentobarbital shortage directed "
        "its main recommendations toward what?",
}


def slug(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:78].rstrip("-")


def load_shards():
    out = {}
    for f in sorted((TOOLS / "shards").rglob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, list):
            for r in d:
                if isinstance(r, dict) and r.get("title"):
                    out.setdefault(r["title"].strip(), (f, r))
    return out


def main():
    orphans = json.loads(Path("/tmp/orph22.json").read_text(encoding="utf-8"))
    for i, stem in RESTEM.items():
        orphans[i]["q"] = stem
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_title = {a["title"].strip(): a for a in cat}
    shards = load_shards()

    added = attached = 0
    for prefix, idxs, page in GROUPS:
        hit = [(t, v) for t, v in shards.items() if t.startswith(prefix[:55])]
        if not hit:
            print(f"  ! no shard record for {prefix[:55]!r} — skipped")
            continue
        title, (shard_file, rec) = hit[0]
        mcqs = [{"q": orphans[i]["q"], "o": orphans[i]["o"],
                 "a": orphans[i]["a"], "e": orphans[i]["e"]} for i in idxs]
        rel = shard_file.relative_to(TOOLS)
        entry = {
            "id": slug(title),
            "title": title,
            "authors": rec.get("authors", "") or "",
            "journal": rec.get("journal", "") or "",
            "year": rec.get("year") or "",
            "citation": " · ".join(
                str(x) for x in (rec.get("authors"), rec.get("journal"), rec.get("year")) if x
            ),
            "doi": "",
            "source": "discovered" if "discovery" in str(rel) else "folder",
            "abstract": rec.get("abstract", "") or "",
            "abstract_origin": f"shard:{rel}",
            "domain": "Physical Health of Animal",
            "subdomain_page": page,
            "mcqs": mcqs,
        }
        if entry["title"] in by_title:
            by_title[entry["title"]]["mcqs"].extend(mcqs)
            print(f"  + {len(mcqs)} MCQ(s) -> existing: {title[:62]}")
        else:
            cat.append(entry)
            print(f"  NEW {title[:62]}  [{entry['journal']} {entry['year']}] +{len(mcqs)} MCQ(s)")
            added += 1

    for i, title in ATTACH.items():
        a = by_title.get(title)
        if not a:
            print(f"  ! catalog article not found: {title[:60]!r}")
            continue
        a.setdefault("mcqs", []).append(
            {"q": orphans[i]["q"], "o": orphans[i]["o"],
             "a": orphans[i]["a"], "e": orphans[i]["e"]}
        )
        attached += 1
        print(f"  + 1 MCQ -> existing: {title[:62]}")

    CATALOG.write_text(
        json.dumps(cat, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n{added} new article(s), {attached} MCQ(s) attached to existing entries; "
          f"catalog now {len(cat)} entries")


if __name__ == "__main__":
    sys.exit(main())
