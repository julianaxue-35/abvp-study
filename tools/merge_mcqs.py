#!/usr/bin/env python3
"""Merge MCQ partial files (tools/mcqs_partials/*.json, each {id: [mcq,...]})
into journal-catalog.json by record id. Reusable across MCQ-generation batches."""
import sys, json, glob, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_catalog as c

CATALOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "journal-catalog.json")
PARTIALS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcqs_partials")


def main():
    d = c.load_catalog(CATALOG)
    by_id = {r["id"]: r for r in d}
    applied = mcq_total = 0
    unmatched = []
    for fp in sorted(glob.glob(os.path.join(PARTIALS, "*.json"))):
        for rid, mcqs in json.load(open(fp)).items():
            if rid in by_id:
                by_id[rid]["mcqs"] = mcqs
                applied += 1
                mcq_total += len(mcqs)
            else:
                unmatched.append((os.path.basename(fp), rid))
    c.save_catalog(CATALOG, d)
    print(f"applied {mcq_total} MCQs to {applied} records")
    if unmatched:
        print("WARNING unmatched ids:", unmatched)
    inv = [(r["id"], c.validate_record(r)) for r in d if c.validate_record(r)]
    print(f"total {len(d)} records | without mcqs {sum(1 for r in d if not r['mcqs'])} | "
          f"total MCQs {sum(len(r['mcqs']) for r in d)} | invalid {len(inv)}")
    for i in inv[:10]:
        print("  INVALID", i)


if __name__ == "__main__":
    main()
