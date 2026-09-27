"""python3 hubdump6.py N [ratio] -> final hub bank items whose correct option is > ratio x the longest distractor (not yet in hubfix/h6*.py)"""
import sys, json, importlib.util, pathlib
H = pathlib.Path(__file__).parent
sys.path.insert(0, str(H)); from hubload import load_hfix
done = set(load_hfix(H, only=lambda s: s.startswith("h6")))
ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 1.2
rows = []
for f in sorted((H/"authoring").glob("*.py")):
    b = H/"banks"/(f.stem+".json")
    if not b.exists(): continue
    bank = {q["q"]: q for q in json.load(open(b))}
    s = importlib.util.spec_from_file_location("a"+f.stem, f); m = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(m)
    except Exception: continue
    for k, it in enumerate(m.ITEMS, 1):
        if it[0] == "keep" or (f.stem, k) in done: continue
        q = bank.get(it[1])
        if not q: continue
        ok = q["o"][q["a"]]; d = [o for i, o in enumerate(q["o"]) if i != q["a"]]
        if len(ok) > ratio * max(map(len, d)) and len(ok) > 40: rows.append((f.stem, k, it[1], ok, d[0], d[1]))
n = int(sys.argv[1]); print(f"# {len(rows)} left")
for s_, k, st, ok, a, b_ in rows[:n]:
    print(f"@{s_}:{k} Q: {st[:130]}\n OK({len(ok)}): {ok}\n A({len(a)}): {a}\n B({len(b_)}): {b_}")
