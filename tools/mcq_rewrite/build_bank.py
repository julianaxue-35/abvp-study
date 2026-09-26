"""usage: python3 build_bank.py authoring/<name>.py  -> banks/<name>.json (+ review html) and QA report.

Authoring file defines:
  PAGE  = "physical-health/surgery_anesthesia_hub.html"
  ITEMS = [ (replaces:[old page-Q indices], stem, correct, wrong1, wrong2, explanation[, tag]), ... ]
Tag (t) and source badge (f) are inherited from replaces[0] unless a tag is given.
"""
import zlib, sys, json, subprocess, random, importlib.util, pathlib, html, re
H = pathlib.Path(__file__).parent
ROOT = H.parent.parent

def load(p):
    spec = importlib.util.spec_from_file_location("auth", p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def main(path):
    path = pathlib.Path(path); m = load(path)
    old = json.loads(subprocess.check_output(["node", str(H / "dump_json.js"), m.PAGE]))
    n = len(m.ITEMS); pos = [i % 3 for i in range(n)]; random.Random(zlib.crc32(path.stem.encode())).shuffle(pos)
    out, used, warn = [], set(), []
    for k, (it, p) in enumerate(zip(m.ITEMS, pos), 1):
        if it[0] == "keep":            # pass an original item through unchanged (e.g. journal-derived)
            used.add(it[1]); out.append(old[it[1]]); continue
        reps, stem, ok, w1, w2, expl = it[:6]; tag = it[6] if len(it) > 6 else None
        for r in reps:
            if r >= len(old): raise SystemExit(f"item {k}: bad old index {r}")
            used.add(r)
        base = old[reps[0]] if reps else {}
        opts = [w1, w2]; opts.insert(p, ok)
        if len({o.strip().lower() for o in opts}) != 3: warn.append(f"{k}: duplicate options")
        if re.search(r"all of the above|none of the above|to be confirmed|\bTBC\b", " ".join(opts), re.I): warn.append(f"{k}: banned option text")
        if max(len(w1), len(w2)) + 20 < len(ok): warn.append(f"{k}: correct answer much longer ({len(ok)} vs {len(w1)}/{len(w2)})")
        d = {"t": tag or base.get("t"), "f": base.get("f"), "q": stem, "o": opts, "a": p, "e": expl}
        out.append({kk: v for kk, v in d.items() if v is not None})
    tagset = {o.get("t") for o in old}; newtags = {o.get("t") for o in out}
    unused = [i for i in range(len(old)) if i not in used]
    (H / "banks").mkdir(exist_ok=True)
    (H / "banks" / (path.stem + ".json")).write_text(json.dumps(out, indent=1, ensure_ascii=False))
    ok_pos = [sum(1 for o in out if o["a"] == i) for i in range(3)]
    longest = sum(1 for o in out if len(o["o"][o["a"]]) > max(len(x) for i, x in enumerate(o["o"]) if i != o["a"]))
    print(f"{m.PAGE}: old {len(old)} -> new {n} | key a/b/c {ok_pos} | correct-longest {longest}/{n} | tags lost: {sorted(tagset - newtags)} | old items not referenced: {len(unused)} {unused[:40]}")
    for w in warn: print("  WARN", w)

main(sys.argv[1])
