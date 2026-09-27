import importlib.util, pathlib, re
H = pathlib.Path(__file__).parent
fx = {}
for p in sorted((H/"hubfix").glob("*.py")):
    s = importlib.util.spec_from_file_location("hf"+p.stem, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); fx.update(m.HFIX)
W = lambda t: set(re.findall(r"[a-z0-9]+", t.lower()))
J = lambda a, b: len(W(a)&W(b))/max(1, len(W(a)|W(b)))
items = {}
for f in sorted((H/"authoring").glob("*.py")):
    s = importlib.util.spec_from_file_location("a"+f.stem, f); m = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(m)
    except Exception: continue
    for k, it in enumerate(m.ITEMS, 1):
        if it[0] != "keep": items[(f.stem, k)] = it
bad = 0
for key, v in fx.items():
    if key not in items: print("MISSING", key); bad += 1; continue
    ok = items[key][2]; ok2 = v[2] if len(v) > 2 else ok
    for i, w in enumerate(v[:2]):
        if J(w, ok) > 0.55 or J(w, ok2) > 0.55: print(f"SIMILAR {key} w{i+1} j={J(w,ok):.2f}\n  OK : {ok}\n  W  : {w}"); bad += 1
    if len(v) > 2 and J(ok2, ok) < 0.5: print(f"OKDRIFT {key}\n  OLD: {ok}\n  NEW: {ok2}"); bad += 1
    if len(ok2) <= max(len(v[0]), len(v[1])) * 0.85: print(f"OKSHORT {key} {len(ok2)} vs {len(v[0])}/{len(v[1])}"); bad += 1
print("flagged", bad, "of", len(fx))
