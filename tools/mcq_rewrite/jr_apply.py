"""Write the rewritten journal MCQs into journal-catalog.json (1 MCQ per article, 3 options)."""
import sys
from jr_lib import *
cat = load_cat(); jr = load_jr(); n = 0
for idx, (stem, ok, w1, w2, expl) in jr.items():
    r = cat[idx]
    o, p = options(r["id"], ok, w1, w2)
    assert len({x.strip().lower() for x in o}) == 3, (idx, "dup options")
    r["mcqs"] = [{"q": stem, "o": o, "a": p, "e": expl}]; r["mcq_v"] = 2; n += 1
save_cat(cat)
left = sum(1 for r in cat if r.get("mcq_v") != 2)
print(f"rewrote {n} articles; {left} of {len(cat)} still on old MCQs")
