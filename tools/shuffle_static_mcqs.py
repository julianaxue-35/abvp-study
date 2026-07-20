#!/usr/bin/env python3
"""shuffle_static_mcqs.py — balance answer positions in static-HTML MCQ banks.

The site-wide Fisher-Yates patch (tools/add_mcq_shuffle.py, commit 035c6ba)
only reaches banks held in a JS array (`var Q=[...]`). Thirteen pages instead
hold their questions as literal markup:

    <div class="q" data-tag="...">
      <div class="meta">...</div>
      <p class="stem">...</p>
      <button class="opt" onclick="ans(this,false)"><span class="k">A</span>…</button>
      ... x4
      <div class="expl"><b class="cor">B is correct.</b> …</div>
    </div>

Those were never shuffled and their correct answers are badly clustered
(one page sits at C=76% with A and D never used).

Unlike the JS banks, these explanations often argue against the distractors
by letter ("Option D is incorrect because…", "Options A, B, and D are all
input-based"). A naive shuffle would leave that prose pointing at the wrong
options, so every letter reference is remapped alongside the buttons.

Usage:
    python3 tools/shuffle_static_mcqs.py --dry      # report only
    python3 tools/shuffle_static_mcqs.py           # rewrite in place
"""
import argparse
import glob
import os
import random
import re
import sys
from collections import Counter

SEED = 20260720  # fixed so reruns are reproducible

Q_RE = re.compile(r'(<div class="q"[^>]*>)(.*?)(\n\s*</div>)', re.S)
OPT_RE = re.compile(
    r'<button class="opt" onclick="ans\(this,(true|false)\)">'
    r'<span class="k">([A-D])</span>(.*?)</button>',
    re.S,
)
COR_RE = re.compile(r'(<b class="cor">)([A-D])( is correct\.</b>)')

# Prose references to options. Two shapes:
#   "Option D", "Options A, B, and D", "option C)", "answer B", "choice A"
#   "D is incorrect", "A is wrong"
LEAD_RE = re.compile(r'\b([Oo]ptions?|[Aa]nswers?|[Cc]hoices?)(\s+)([A-D])\b')
LIST_TAIL_RE = re.compile(r'\A((?:\s*,\s*|\s+and\s+|\s*,\s*and\s+))([A-D])\b')
BARE_RE = re.compile(r'\b([A-D])(\s+is\s+(?:wrong|incorrect))', re.I)


def remap_prose(text, mapping):
    """Rewrite option-letter references using mapping{old_letter: new_letter}.

    Single left-to-right pass: a phrase like "(option C is incorrect)" matches
    both LEAD_RE and BARE_RE, so running them as two passes would remap that
    letter twice and leave the sentence pointing at the wrong distractor.
    """
    out = []
    i = 0
    while i < len(text):
        lead = LEAD_RE.search(text, i)
        bare = BARE_RE.search(text, i)
        # take whichever reference comes first; LEAD wins ties (it starts earlier)
        if lead and (not bare or lead.start() <= bare.start()):
            out.append(text[i:lead.start()])
            out.append(lead.group(1) + lead.group(2) + mapping[lead.group(3)])
            j = lead.end()
            # consume a trailing enumeration: "A, B, and D"
            while True:
                t = LIST_TAIL_RE.match(text, j)
                if not t:
                    break
                out.append(t.group(1) + mapping[t.group(2)])
                j = t.end()
            i = j
        elif bare:
            out.append(text[i:bare.start()])
            out.append(mapping[bare.group(1).upper()] + bare.group(2))
            i = bare.end()
        else:
            break
    out.append(text[i:])
    return "".join(out)


def targets(n, rng):
    """Correct-answer positions: even 25% split, order randomised."""
    seq = [i % 4 for i in range(n)]
    rng.shuffle(seq)
    return seq


def process(path, rng, dry):
    src = open(path, encoding="utf-8").read()
    blocks = list(Q_RE.finditer(src))
    usable = []
    for m in blocks:
        opts = OPT_RE.findall(m.group(2))
        if len(opts) == 4 and [o[0] for o in opts].count("true") == 1:
            usable.append((m, opts))
    if not usable:
        return None

    want = targets(len(usable), rng)
    out, cursor, changed = [], 0, 0
    for (m, opts), tgt in zip(usable, want):
        body = m.group(2)
        cor_old = [o[0] for o in opts].index("true")
        order = [i for i in range(4) if i != cor_old]
        rng.shuffle(order)
        order.insert(tgt, cor_old)
        # mapping: old displayed letter -> new displayed letter
        mapping = {opts[old][1]: "ABCD"[new] for new, old in enumerate(order)}

        rebuilt = []
        for new, old in enumerate(order):
            flag = "true" if old == cor_old else "false"
            rebuilt.append(
                f'<button class="opt" onclick="ans(this,{flag})">'
                f'<span class="k">{"ABCD"[new]}</span>{opts[old][2]}</button>'
            )
        # splice the new buttons over the span the old ones occupied
        first = OPT_RE.search(body)
        last = None
        for last in OPT_RE.finditer(body):
            pass
        joiner = body[first.end():OPT_RE.search(body, first.end()).start()]
        new_body = body[:first.start()] + joiner.join(rebuilt) + body[last.end():]
        new_body = COR_RE.sub(
            lambda c: c.group(1) + "ABCD"[tgt] + c.group(3), new_body, count=1
        )
        # remap distractor references inside the explanation prose only
        e = re.search(r'(<div class="expl">)(.*?)(</div>)', new_body, re.S)
        if e:
            head, prose, tail = e.groups()
            lead = COR_RE.search(prose)
            split = lead.end() if lead else 0
            fixed = prose[:split] + remap_prose(prose[split:], mapping)
            new_body = new_body[:e.start()] + head + fixed + tail + new_body[e.end():]

        if new_body != body:
            changed += 1
        out.append(src[cursor:m.start(2)])
        out.append(new_body)
        cursor = m.end(2)
    out.append(src[cursor:])
    result = "".join(out)

    if not dry:
        open(path, "w", encoding="utf-8").write(result)
    return len(usable), changed, result


def dist(text):
    d = Counter()
    for m in Q_RE.finditer(text):
        opts = OPT_RE.findall(m.group(2))
        if len(opts) == 4 and [o[0] for o in opts].count("true") == 1:
            d["ABCD"[[o[0] for o in opts].index("true")]] += 1
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--page")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    files = [args.page] if args.page else sorted(glob.glob("*/*.html"))

    rng = random.Random(SEED)
    total = 0
    for f in files:
        before = dist(open(f, encoding="utf-8").read())
        if not before:
            continue
        res = process(f, rng, args.dry)
        if not res:
            continue
        n, changed, text = res
        after = dist(text)
        b = " ".join(f"{k}:{before.get(k,0)*100//n:>2}%" for k in "ABCD")
        a = " ".join(f"{k}:{after.get(k,0)*100//n:>2}%" for k in "ABCD")
        print(f"{n:>4} q  [{b}] -> [{a}]  {f}")
        total += n
    print(f"\n{'would rewrite' if args.dry else 'rewrote'} {total} questions")


if __name__ == "__main__":
    sys.exit(main())
