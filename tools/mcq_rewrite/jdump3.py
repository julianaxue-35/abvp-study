"""python3 jdump3.py N -> items whose correct option is >25% longer than the longest distractor and not yet in jr3/"""
import sys, importlib.util
from jr_lib import *
done=set()
for p in (H/"jr3").glob("*.py"):
    spec=importlib.util.spec_from_file_location("y"+p.stem,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    done|={i[0] for i in m.JITEMS3}
jr=load_jr()
ks=[k for k in sorted(jr) if k not in done and len(jr[k][1])>1.25*max(len(jr[k][2]),len(jr[k][3]))]
n=int(sys.argv[1]); print(f"# {len(ks)} left")
for k in ks[:n]:
    st,ok,w1,w2,e=jr[k]; print(f"#{k} Q: {st[:130]}\n OK({len(ok)}): {ok}\n X1({len(w1)}): {w1}\n X2({len(w2)}): {w2}")
