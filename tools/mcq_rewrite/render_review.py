"""Render pilot_infectious_disease.json -> review_infectious_disease.html (self-contained)."""
import json, html, pathlib
H = pathlib.Path(__file__).parent
items = json.loads((H / "pilot_infectious_disease.json").read_text())
e = html.escape
topics = []
for it in items:
    if it["topic"] not in topics: topics.append(it["topic"])
body = []
for t in topics:
    body.append(f"<h2>{e(t)}</h2>")
    for it in [i for i in items if i["topic"] == t]:
        opts = "".join(
            f'<li class="{"key" if k == it["a"] else ""}"><b>{"abc"[k]}.</b> {e(o)}</li>'
            for k, o in enumerate(it["o"]))
        old = "".join(
            f'<div class="old"><i>#{r["idx"]}</i> {e(r.get("q","?"))} <span>&rarr; {e(r.get("a",""))}</span></div>'
            for r in it["replaces"])
        body.append(f'''<section class="q"><div class="num">{it["n"]}</div><div>
<p class="stem">{e(it["q"])}</p><ol type="a">{opts}</ol>
<p class="exp"><b>Why:</b> {e(it["e"])}</p>
<details><summary>Replaces {len(it["replaces"])} old question(s)</summary>{old}</details></div></section>''')
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Infectious Disease MCQ pilot</title><style>
:root{{--bg:#fff;--fg:#1c2b22;--mut:#5b6b62;--line:#d7e0da;--key:#e3f4e8;--acc:#1f5c3a}}
@media(prefers-color-scheme:dark){{:root{{--bg:#15201a;--fg:#e6efe9;--mut:#9fb0a6;--line:#2c3b33;--key:#1f3a2a;--acc:#7fd1a0}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:820px;margin:0 auto;padding:16px}}
h1{{font-size:1.4rem}}h2{{margin-top:2rem;border-bottom:2px solid var(--acc);padding-bottom:.2rem;color:var(--acc)}}
.q{{display:flex;gap:12px;border:1px solid var(--line);border-radius:8px;padding:12px;margin:12px 0}}
.num{{font-weight:700;color:var(--acc);min-width:1.8rem}}.stem{{margin:0 0 .5rem;font-weight:600}}
ol{{list-style:none;padding:0;margin:0}}li{{padding:4px 8px;border-radius:6px;margin:2px 0}}li.key{{background:var(--key)}}
.exp{{color:var(--mut);font-size:.92rem}}details{{font-size:.88rem;color:var(--mut)}}.old{{margin:4px 0;padding-left:8px;border-left:3px solid var(--line)}}.old span{{color:var(--fg)}}
</style></head><body><h1>Infectious Disease MCQ pilot ({len(items)} items)</h1>
<p>Three options, one correct answer (shaded), two plausible distractors. Old questions each item replaces are under &ldquo;Replaces&rdquo;. Nothing here is live.</p>
{"".join(body)}</body></html>'''
(H / "review_infectious_disease.html").write_text(page)
print("ok", len(page))
