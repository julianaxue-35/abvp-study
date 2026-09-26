"""usage: python3 patch.py authoring/x.py patches.txt  (blocks: OLD ⟹ NEW, one per line)"""
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text(); miss = 0
for ln in pathlib.Path(sys.argv[2]).read_text().splitlines():
    if " ⟹ " not in ln: continue
    a, b = ln.split(" ⟹ ", 1)
    if a not in s: print("MISSING:", a[:70]); miss += 1; continue
    s = s.replace(a, b)
p.write_text(s); print("patched, missing", miss)
