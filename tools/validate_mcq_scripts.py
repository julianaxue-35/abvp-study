#!/usr/bin/env python3
"""Extract every <script> block from each MCQ file and node --check it."""
import re, io, subprocess, sys, os, tempfile

files = [l.strip().lstrip("./") for l in open("/tmp/mcq_files.txt") if l.strip()]
bad = 0
for f in files:
    s = io.open(f, encoding='utf-8').read()
    # grab inline script blocks (skip ones with src=)
    blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', s, re.DOTALL)
    failed = False
    for bi, js in enumerate(blocks):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tmp:
            tmp.write(js); tmppath = tmp.name
        r = subprocess.run(["node", "--check", tmppath], capture_output=True, text=True)
        os.unlink(tmppath)
        if r.returncode != 0:
            failed = True
            print(f"FAIL {f} [block {bi}]")
            for line in r.stderr.strip().splitlines()[:4]:
                print("     " + line)
    if failed:
        bad += 1
    else:
        print(f"ok   {f}")
print(f"\n{'ALL OK' if bad==0 else str(bad)+' FILE(S) FAILED'}")
sys.exit(1 if bad else 0)
