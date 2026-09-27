"""python3 hubdump.py N [minratio] -> hub authoring items whose correct option is longer than minratio x the longest distractor, not yet in hubfix/"""
import sys, importlib.util, pathlib
H = pathlib.Path(__file__).parent
done = set()
for p in sorted((H/"hubfix").glob("*.py")):
    spec = importlib.util.spec_from_file_location("hf"+p.stem, p); mm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mm); done |= set(mm.HFIX)
n = int(sys.argv[1]); mr = float(sys.argv[2]) if len(sys.argv) > 2 else 1.12
rows = []
for f in sorted((H/"authoring").glob("*.py")):
    spec = importlib.util.spec_from_file_location("a"+f.stem, f); m = importlib.util.module_from_spec(spec)
    try: spec.loader.exec_module(m)
    except Exception: continue
    for k, it in enumerate(m.ITEMS, 1):
        if it[0] == "keep": continue
        reps, stem, ok, w1, w2 = it[:5]
        if (f.stem, k) in done: continue
        import zlib
        if zlib.crc32(f'{f.stem}:{k}'.encode()) % 3 == 0: continue   # rule: ~1/3 of items may keep the correct option longest
        if len(ok) > 20 and len(ok) > mr * max(len(w1), len(w2)): rows.append((f.stem, k, stem, ok, w1, w2))
print(f"# {len(rows)} left")
for s, k, st, ok, w1, w2 in rows[:n]:
    print(f"@{s}:{k} Q: {st[:150]}\n OK({len(ok)}): {ok}\n X1({len(w1)}): {w1}\n X2({len(w2)}): {w2}")
