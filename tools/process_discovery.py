#!/usr/bin/env python3
"""Process web-discovered article partials into journal-catalog.json.

Reads tools/discovery_partials/{jsmcah,other_*}.json (LIST of records with
real abstracts + mcqs), applies fabrication guard, year filter, dedupe, slug
+ subdomain mapping, validation, then appends NEW records to the catalog.

recovered.json is intentionally EXCLUDED (its abstracts are reconstructed /
duplicates — not exam-eligible).
"""
import sys, os, json, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib_catalog as c
import extract_folder as ef

CATALOG = os.path.join(HERE, "journal-catalog.json")
PARTDIR = os.path.join(HERE, "discovery_partials")

# Precise fabrication signatures (substring match on lowercased abstract).
FAB_SIGS = [
    "reconstructed", "faithfully reconstructed",
    "does not carry a formal", "does not carry a structured",
    "does not carry a traditional", "no formal structured abstract",
    "no formal abstract", "no structured abstract",
]


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def mcq_ok(m):
    return (
        isinstance(m, dict)
        and isinstance(m.get("q"), str) and m["q"].strip()
        and isinstance(m.get("o"), list) and len(m["o"]) == 4
        and all(isinstance(o, str) and o.strip() for o in m["o"])
        and isinstance(m.get("a"), int) and not isinstance(m.get("a"), bool) and 0 <= m["a"] < 4
        and isinstance(m.get("e"), str) and m["e"].strip()
    )


def main():
    cat = c.load_catalog(CATALOG)
    existing_titles = {norm_title(r["title"]) for r in cat}
    existing_dois = {(r.get("doi") or "").strip().lower() for r in cat if (r.get("doi") or "").strip()}
    existing_ids = {r["id"] for r in cat}

    files = sorted(
        f for f in glob.glob(os.path.join(PARTDIR, "*.json"))
        if os.path.basename(f) != "recovered.json"
    )

    added, skipped = [], []
    seen_titles = set()
    for f in files:
        try:
            recs = json.load(open(f))
        except Exception as e:
            skipped.append((os.path.basename(f), "-", f"unreadable: {e}"))
            continue
        if not isinstance(recs, list):
            continue
        for r in recs:
            title = (r.get("title") or "").strip()
            ab = (r.get("abstract") or "").strip()
            why = None
            if not title or not ab:
                why = "missing title/abstract"
            elif ab.lstrip().upper().startswith("NOTE"):
                why = "fabrication: NOTE-prefixed"
            elif any(s in ab.lower() for s in FAB_SIGS):
                why = "fabrication: reconstructed-signature"
            else:
                year = r.get("year")
                try:
                    year = int(year)
                except Exception:
                    year = None
                if year is None or not (2021 <= year <= 2026):
                    why = f"year out of window ({r.get('year')})"
                else:
                    nt = norm_title(title)
                    doi = (r.get("doi") or "").strip().lower()
                    if nt in existing_titles or nt in seen_titles:
                        why = "duplicate title"
                    elif doi and doi in existing_dois:
                        why = "duplicate doi"
            if why:
                skipped.append((os.path.basename(f), title[:70], why))
                continue

            # passed filters — build record
            abstract = ef.clean_abstract(ab) or ab
            mcqs = [m for m in (r.get("mcqs") or []) if mcq_ok(m)]
            authors = (r.get("authors") or "").strip()
            journal = (r.get("journal") or "").strip()
            doi = (r.get("doi") or "").strip()
            page, domain, note = ef.guess_subdomain(title, abstract)
            slug = ef.dedupe_slug(ef.make_slug(title), existing_ids)
            existing_ids.add(slug)
            rec = {
                "id": slug,
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": int(r["year"]),
                "citation": ef.build_citation(title, authors, journal, int(r["year"]), doi),
                "doi": doi,
                "source": "discovered",
                "abstract": abstract,
                "abstract_origin": "url:" + (r.get("source_url") or "").strip(),
                "domain": domain,
                "subdomain_page": page,
                "mcqs": mcqs,
            }
            probs = c.validate_record(rec)
            if probs:
                skipped.append((os.path.basename(f), title[:70], f"invalid: {probs}"))
                continue
            if not mcqs:
                skipped.append((os.path.basename(f), title[:70], "no valid mcqs"))
                continue
            seen_titles.add(norm_title(title))
            if doi:
                existing_dois.add(doi.lower())
            rec["_unmapped"] = bool(note)  # transient flag for reporting
            added.append(rec)

    # write unmapped review list, then strip the transient flag before saving
    unmapped = [r for r in added if r.get("_unmapped")]
    for r in added:
        r.pop("_unmapped", None)

    cat.extend(added)
    c.save_catalog(CATALOG, cat)

    print(f"ADDED {len(added)} discovered records ({sum(len(r['mcqs']) for r in added)} MCQs)")
    print(f"SKIPPED {len(skipped)}")
    inv = [(r["id"], c.validate_record(r)) for r in cat if c.validate_record(r)]
    print(f"catalog total {len(cat)} | invalid {len(inv)} | without mcqs {sum(1 for r in cat if not r['mcqs'])}")

    with open(os.path.join(PARTDIR, "discovery_merge_log.md"), "w") as fh:
        fh.write("# Discovery merge log\n\n")
        fh.write(f"Added: {len(added)} | Skipped: {len(skipped)}\n\n")
        fh.write("## Unmapped (defaulted subdomain — review)\n\n")
        for r in unmapped:
            fh.write(f"- {r['title']}  ->  {r['subdomain_page']}\n")
        fh.write("\n## Skipped\n\n")
        for src, t, why in skipped:
            fh.write(f"- [{src}] {t} — {why}\n")
    print(f"unmapped(defaulted): {len(unmapped)} — see discovery_merge_log.md")


if __name__ == "__main__":
    main()
