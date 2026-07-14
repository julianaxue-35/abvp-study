#!/usr/bin/env python3
import re, io, sys, os

MARKER = "/*mcq-shuffle*/"
VARS = ["Q", "JQ", "JJ"]

def snippet(var):
    return (MARKER + "(function(){var _a=" + var + ";if(!Array.isArray(_a))return;"
            "for(var _i=0;_i<_a.length;_i++){var _q=_a[_i];"
            "if(!_q||!Array.isArray(_q.o)||typeof _q.a!=='number')continue;"
            "var _c=_q.o[_q.a];"
            "for(var _j=_q.o.length-1;_j>0;_j--){var _k=Math.floor(Math.random()*(_j+1));"
            "var _t=_q.o[_j];_q.o[_j]=_q.o[_k];_q.o[_k]=_t;}"
            "_q.a=_q.o.indexOf(_c);}})();")

def find_array_end(s, br):
    """br = index of the opening '['; return index of matching ']' (string-aware)."""
    depth = 0; i = br; n = len(s)
    while i < n:
        c = s[i]
        if c == '"' or c == "'":
            q = c; i += 1
            while i < n:
                if s[i] == '\\': i += 2; continue
                if s[i] == q: break
                i += 1
        elif c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def inject_file(path):
    s = io.open(path, encoding='utf-8').read()
    injected = []
    for var in VARS:
        m = re.search(r'(?:const|var|let)\s+' + re.escape(var) + r'\s*=\s*\[', s)
        if not m:
            continue
        br = s.index('[', m.end() - 1)
        end = find_array_end(s, br)
        if end == -1:
            print(f"  !! {var}: array end not found in {path}")
            continue
        j = end + 1
        while j < len(s) and s[j] in ' \t':
            j += 1
        insert_at = j + 1 if (j < len(s) and s[j] == ';') else end + 1
        # idempotency: skip if a shuffle for this var already sits right here
        if s[insert_at:insert_at + 400].startswith(MARKER):
            continue
        s = s[:insert_at] + snippet(var) + s[insert_at:]
        injected.append(var)
    if injected:
        io.open(path, 'w', encoding='utf-8').write(s)
    return injected

if __name__ == "__main__":
    files = [l.strip() for l in open("/tmp/mcq_files.txt") if l.strip()]
    skip = "shelter-management/01_population_management.html"  # already has manual shuffle
    total = 0
    for f in files:
        f = f[2:] if f.startswith("./") else f
        if f.endswith(skip):
            print(f"SKIP (manual) {f}")
            continue
        inj = inject_file(f)
        if inj:
            total += len(inj)
            print(f"OK {f}: {'+'.join(inj)}")
        else:
            print(f"-- {f}: nothing injected")
    print(f"\nTotal shuffle blocks injected: {total}")
