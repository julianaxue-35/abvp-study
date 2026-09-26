"""Flag original items whose keyed option overlaps the explanation much less than another option does."""
import json, re, glob, pathlib
STOP = set("the a an of to and or in on for is are be by with as at that this it its from which not no than then their they can may will was were has have had into over under only also more most".split())
def toks(s): return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}
out = []
for f in sorted(glob.glob("orig/*.json")):
    d = json.load(open(f))
    for i, q in enumerate(d):
        e = toks(q["e"]); 
        if not e: continue
        sc = [len(toks(o) & e) for o in q["o"]]
        best = max(range(len(sc)), key=lambda k: sc[k])
        if best != q["a"] and sc[best] >= 4 and sc[q["a"]] <= 0.34 * sc[best] and sorted(sc)[-2] < sc[best]:
            out.append((f.replace("orig/", "").replace(".html.json", ""), i, "abcd"[q["a"]], "abcd"[best], round(sc[q["a"]], 2), round(sc[best], 2), q["q"][:80], q["o"][q["a"]][:60], q["o"][best][:60]))
for r in out: print(*r, sep=" | ")
print(len(out), "suspect items")
