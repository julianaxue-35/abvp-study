"""python3 hubdump5.py N -> hub items (authoring + hubfix) where a distractor has an absolute word and the correct option has none (not yet in hubfix/h5*.py)"""
import sys, re, importlib.util, pathlib
H = pathlib.Path(__file__).parent
R = re.compile(r"\b(never|always|only|all|none|every|entirely|completely|solely|cannot|impossible|guarantee[sd]?|regardless|invariably|universally|exclusively|purely|absolutely|identical|almost all|no (?:difference|effect|benefit|role|change|relationship|association))\b", re.I)
sys.path.insert(0, str(H)); from hubload import load_hfix
fx = load_hfix(H); done = set(load_hfix(H, only=lambda s: s.startswith("h5")))
rows = []
for f in sorted((H/"authoring").glob("*.py")):
    s = importlib.util.spec_from_file_location("a"+f.stem, f); m = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(m)
    except Exception: continue
    for k, it in enumerate(m.ITEMS, 1):
        if it[0] == "keep" or (f.stem, k) in done: continue
        stem, ok, w1, w2 = it[1:5]; v = fx.get((f.stem, k))
        if v: w1, w2 = (v[0] if v[0] is not None else w1), (v[1] if v[1] is not None else w2); ok = v[2] if len(v) > 2 else ok
        if not R.search(ok) and (R.search(w1) or R.search(w2)): rows.append((f.stem, k, stem, ok, w1, w2))
n = int(sys.argv[1]); print(f"# {len(rows)} left")
for s, k, st, ok, w1, w2 in rows[:n]:
    print(f"@{s}:{k} Q: {st[:150]}\n OK: {ok}\n A{'*' if R.search(w1) else ''}: {w1}\n B{'*' if R.search(w2) else ''}: {w2}")
