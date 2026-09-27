"""python3 jdump5.py N -> journal items where a distractor has an absolute word and the correct option has none (not yet in jr5)"""
import sys, re, importlib.util
from jr_lib import *
R = re.compile(r"\b(never|always|only|all|none|every|entirely|completely|solely|cannot|impossible|guarantee[sd]?|regardless|invariably|universally|exclusively|purely|absolutely|identical|almost all|no (?:difference|effect|benefit|role|change|relationship|association))\b", re.I)
done = set()
for p in (H/"jr5").glob("*.py"):
    spec = importlib.util.spec_from_file_location("z"+p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); done |= {i[0] for i in m.JITEMS5}
jr = load_jr()
ks = [k for k in sorted(jr) if k not in done and not R.search(jr[k][1]) and (R.search(jr[k][2]) or R.search(jr[k][3]))]
n = int(sys.argv[1]); print(f"# {len(ks)} left")
for k in ks[:n]:
    st, ok, w1, w2, e = jr[k]
    print(f"#{k} Q: {st[:170]}\n OK: {ok}\n A{'*' if R.search(w1) else ''}: {w1}\n B{'*' if R.search(w2) else ''}: {w2}")
