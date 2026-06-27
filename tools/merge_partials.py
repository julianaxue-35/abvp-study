#!/usr/bin/env python3
"""Merge lean workflow partials into journal-catalog.json.

Each partial record is LEAN: {idx, domain, subdomain_page, authors, journal, mcqs}.
We join by `idx` to the worklist to restore the VERBATIM title/abstract/year/source/
abstract_origin, then build the citation + a unique id deterministically.

Usage:
  python3 tools/merge_partials.py --partials "qa_fixes/folder_batch_*.json" \
                                  --worklist tools/folder_new_articles.json
"""
import argparse
import glob
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))
from lib_catalog import load_catalog, save_catalog, validate_record
from lib_extract import norm_title, author_lastname

_STOP = {"the", "a", "an", "of", "in", "on", "and", "for", "to", "with",
         "using", "study", "from", "by", "at", "as", "is", "are"}


def slug(authors, year, title):
    al = author_lastname(authors) or "anon"
    words = [w for w in re.findall(r"[a-z0-9]+", str(title).lower()) if w not in _STOP]
    return "-".join([al, str(year)] + words[:4]) or f"{al}-{year}"


def build_record(lean, src):
    title = src["title"]
    year = src["year"]
    authors = (lean.get("authors") or src.get("authors") or "").strip()
    journal = (lean.get("journal") or src.get("journal") or "").strip()
    citation = ". ".join([p for p in [authors, title, journal, str(year)] if p]).strip()
    if not citation.endswith("."):
        citation += "."
    return {
        "id": slug(authors, year, title),
        "title": title,
        "authors": authors,
        "journal": journal,
        "year": year,
        "citation": citation,
        "doi": "",
        "source": src.get("source", "folder"),
        "abstract": src["abstract"],
        "abstract_origin": src.get("abstract_origin", "spreadsheet"),
        "domain": lean["domain"],
        "subdomain_page": lean["subdomain_page"],
        "mcqs": lean.get("mcqs", []),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partials", required=True, help="glob (relative to cwd) of partial JSON files")
    ap.add_argument("--worklist", required=True, help="worklist JSON with idx-ordered source records")
    args = ap.parse_args()

    cat = load_catalog(str(TOOLS / "journal-catalog.json"))
    have_titles = {norm_title(r["title"]) for r in cat}
    have_ids = {r["id"] for r in cat}

    worklist = json.loads(Path(args.worklist).read_text(encoding="utf-8"))
    files = sorted(glob.glob(args.partials))
    if not files:
        print(f"no partials match {args.partials!r}")
        sys.exit(1)

    lean_recs = []
    for f in files:
        lean_recs.extend(json.loads(Path(f).read_text(encoding="utf-8")))

    added, problems, skipped_idx = [], [], []
    seen_idx = set()
    for lean in lean_recs:
        idx = lean.get("idx")
        if idx is None or idx >= len(worklist):
            problems.append((f"idx={idx}", ["idx missing or out of range"]))
            continue
        if idx in seen_idx:
            continue
        seen_idx.add(idx)
        src = worklist[idx]
        n = norm_title(src["title"])
        if n in have_titles:
            continue  # last-line dedup safety
        rec = build_record(lean, src)
        base = rec["id"]
        k = 1
        while rec["id"] in have_ids:
            rec["id"] = f"{base}-{k}"
            k += 1
        errs = validate_record(rec)
        if errs:
            problems.append((rec.get("title", "?")[:60], errs))
            continue
        have_titles.add(n)
        have_ids.add(rec["id"])
        added.append(rec)

    missing = [i for i in range(len(worklist)) if i not in seen_idx
               and norm_title(worklist[i]["title"]) not in {norm_title(r["title"]) for r in cat}]

    if problems:
        for t, e in problems[:25]:
            print("INVALID:", t, e)
        print(f"\n{len(problems)} invalid records — fix partials and re-run. Nothing written.")
        sys.exit(1)

    save_catalog(str(TOOLS / "journal-catalog.json"), cat + added)
    print(f"appended {len(added)} records; catalog now {len(cat) + len(added)}")
    if missing:
        print(f"NOTE: {len(missing)} worklist indices produced no record (idx: {missing[:20]}{'…' if len(missing) > 20 else ''})")


if __name__ == "__main__":
    main()
