"""Shared helpers for the journal-MCQ rewrite. jr/<page__slug>__NN.py files define JITEMS = [(catalog_idx, stem, correct, wrong1, wrong2, explanation), ...]."""
import json, pathlib, importlib.util, zlib
H = pathlib.Path(__file__).parent
CAT = H.parent / "journal-catalog.json"

def load_cat():
    return json.load(open(CAT, encoding="utf-8"))

def save_cat(c):
    with open(CAT, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1); f.write("\n")

def load_jr():
    """{catalog_idx: (stem, ok, w1, w2, expl)} from every jr/*.py file"""
    out = {}
    for p in sorted((H / "jr").glob("*.py")):
        spec = importlib.util.spec_from_file_location(p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for it in m.JITEMS:
            if it[0] in out: raise SystemExit(f"duplicate catalog idx {it[0]} in {p.name}")
            out[it[0]] = tuple(it[1:6])
    for p in sorted((H / "jr2").glob("*.py")):
        spec = importlib.util.spec_from_file_location("jr2_" + p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for it in m.JITEMS2:  # (idx, ok, w1, w2, expl[, stem]) -- length-balanced override of a jr/ item
            st = it[5] if len(it) > 5 else out[it[0]][0]
            out[it[0]] = (st, it[1], it[2], it[3], it[4])
    for p in sorted((H / "jr3").glob("*.py")):
        spec = importlib.util.spec_from_file_location("jr3_" + p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for it in m.JITEMS3:  # (idx, w1, w2[, ok]) -- re-parallelised distractors (and optionally a tighter correct option)
            st, ok, w1, w2, e = out[it[0]]
            out[it[0]] = (st, it[3] if len(it) > 3 else ok, it[1], it[2], e)
    for p in sorted((H / "jr4").glob("*.py")):
        spec = importlib.util.spec_from_file_location("jr4_" + p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for it in m.JITEMS4:  # (idx, "A"|"B", suffix) appends an elaboration clause to a distractor, applied before the trim pass
            st, ok, w1, w2, e = out[it[0]]
            if it[1] == "A": w1 = w1.rstrip(".") + it[2]
            else: w2 = w2.rstrip(".") + it[2]
            out[it[0]] = (st, ok, w1, w2, e)
    # final length-tell pass: for ~2/3 of items keep the correct option from being the longest by trimming a trailing elaboration clause
    from jr_trim import trim, want_longest
    cat = load_cat()
    for k, (st, ok, w1, w2, e) in list(out.items()):
        lim = max(len(w1), len(w2))
        if len(ok) > lim and not want_longest(cat[k]["id"]):
            out[k] = (st, trim(ok, lim), w1, w2, e)
    return out

def options(rec_id, ok, w1, w2):
    p = zlib.crc32(rec_id.encode()) % 3
    o = [w1, w2]; o.insert(p, ok); return o, p
