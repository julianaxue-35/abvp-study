"""python3 jdump.py START N -> compact dump of jr items (sorted by idx) after the ones already overridden in jr2/"""
import sys, importlib.util
from jr_lib import *
done=set()
for p in (H/"jr2").glob("*.py"):
    spec=importlib.util.spec_from_file_location("x"+p.stem,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    done|={i[0] for i in m.JITEMS2}
jr=load_jr(); ks=[k for k in sorted(jr) if k not in done]
n=int(sys.argv[1]) if len(sys.argv)>1 else 60
print(f"# {len(ks)} left")
for k in ks[:n]:
    st,ok,w1,w2,e=jr[k]; print(f"#{k} Q: {st}\n  OK: {ok}\n  X1: {w1}\n  X2: {w2}\n  E: {e}")
