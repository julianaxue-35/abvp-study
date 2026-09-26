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
    return out

def options(rec_id, ok, w1, w2):
    p = zlib.crc32(rec_id.encode()) % 3
    o = [w1, w2]; o.insert(p, ok); return o, p
