import importlib.util, pathlib
H = pathlib.Path(__file__).parent
fx = {}
for p in sorted((H/"hubfix").glob("*.py")):
    s = importlib.util.spec_from_file_location("hf"+p.stem, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); fx.update(m.HFIX)
n = lg = sh = 0
for f in sorted((H/"authoring").glob("*.py")):
    s = importlib.util.spec_from_file_location("a"+f.stem, f); m = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(m)
    except Exception: continue
    for k, it in enumerate(m.ITEMS, 1):
        if it[0] == "keep": continue
        ok, w1, w2 = it[2:5]
        v = fx.get((f.stem, k))
        if v: w1, w2 = v[0], v[1]; ok = v[2] if len(v) > 2 else ok
        n += 1; lg += len(ok) > max(len(w1), len(w2)); sh += len(ok) < min(len(w1), len(w2))
print(n, f"longest {lg/n:.1%} shortest {sh/n:.1%}")
