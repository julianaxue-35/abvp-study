"""Length-tell fix: pseudo-randomly (crc32 of article id) decide whether the correct option may be the longest;
if it must not be, trim trailing elaboration clause(s) from the correct option until it is no longer than the longest distractor."""
import re, zlib, sys
CONN = [", so ", ", with ", ", while ", ", though ", ", but ", ", despite ", ", which ", ", and only ", ", whereas ", "; "]
def trim(ok, limit):
    t = ok
    while len(t) > limit:
        cut = -1
        for c in CONN:
            i = t.rfind(c)
            if i > cut: cut = i
        if cut < 0: break
        nt = t[:cut]
        if len(nt) < 30 or len(nt) < 0.45 * len(ok): break
        t = nt
    return t
def want_longest(rid):
    return zlib.crc32((rid + "|len").encode()) % 3 == 0   # ~1/3 of items keep correct as longest
