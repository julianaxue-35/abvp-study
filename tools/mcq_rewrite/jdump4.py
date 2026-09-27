"""items where correct is still the longest and the crc rule says it should not be; prints the two distractors so one can be lengthened (jr4)"""
import sys, importlib.util
from jr_lib import *; from jr_trim import want_longest
done=set()
for p in (H/"jr4").glob("*.py"):
    spec=importlib.util.spec_from_file_location("z"+p.stem,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    done|={i[0] for i in m.JITEMS4}
jr=load_jr(); cat=load_cat()
ks=[k for k in sorted(jr) if k not in done and len(jr[k][1])>=max(len(jr[k][2]),len(jr[k][3])) and not want_longest(cat[k]["id"])]
n=int(sys.argv[1]); print(f"# {len(ks)} left")
for k in ks[:n]:
    st,ok,w1,w2,e=jr[k]; print(f"#{k} OK({len(ok)}): {ok}\n A({len(w1)}): {w1}\n B({len(w2)}): {w2}")
